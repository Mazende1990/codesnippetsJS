const errors = require('./errors');
const debug = require('debug')('node-telegram-bot-api');
const https = require('https');
const http = require('http');
const fs = require('fs');
const bl = require('bl');
const Promise = require('bluebird');

/**
 * TelegramBotWebHook - Sets up a webhook to receive Telegram Bot updates
 * @see https://core.telegram.org/bots/api#getting-updates
 */
class TelegramBotWebHook {
  /**
   * Creates a new webhook instance
   * @param {TelegramBot} bot - The Telegram bot instance
   */
  constructor(bot) {
    this.bot = bot;
    this._open = false;
    
    // Initialize options with defaults
    this._initializeOptions(bot);
    
    // Bind methods to preserve 'this' context
    this._requestListener = this._requestListener.bind(this);
    this._parseBody = this._parseBody.bind(this);
    
    // Create appropriate server based on configuration
    this._createWebServer();
  }

  /**
   * Initialize webhook options with defaults
   * @private
   * @param {TelegramBot} bot - The Telegram bot instance
   */
  _initializeOptions(bot) {
    this.options = (typeof bot.options.webHook === 'boolean') ? {} : bot.options.webHook;
    this.options.host = this.options.host || '0.0.0.0';
    this.options.port = this.options.port || 8443;
    this.options.https = this.options.https || {};
    this.options.healthEndpoint = this.options.healthEndpoint || '/healthz';
    this._healthRegex = new RegExp(this.options.healthEndpoint);
  }

  /**
   * Create the appropriate web server based on configuration
   * @private
   */
  _createWebServer() {
    if (this.options.key && this.options.cert) {
      debug('HTTPS WebHook enabled (by key/cert)');
      this.options.https.key = fs.readFileSync(this.options.key);
      this.options.https.cert = fs.readFileSync(this.options.cert);
      this._webServer = https.createServer(this.options.https, this._requestListener);
    } else if (this.options.pfx) {
      debug('HTTPS WebHook enabled (by pfx)');
      this.options.https.pfx = fs.readFileSync(this.options.pfx);
      this._webServer = https.createServer(this.options.https, this._requestListener);
    } else if (Object.keys(this.options.https).length) {
      debug('HTTPS WebHook enabled by (https)');
      this._webServer = https.createServer(this.options.https, this._requestListener);
    } else {
      debug('HTTP WebHook enabled');
      this._webServer = http.createServer(this._requestListener);
    }
  }

  /**
   * Open WebHook by listening on the configured port
   * @return {Promise} Resolves when server is listening
   */
  open() {
    if (this.isOpen()) {
      return Promise.resolve();
    }
    
    return new Promise(resolve => {
      this._webServer.listen(this.options.port, this.options.host, () => {
        debug('WebHook listening on port %s', this.options.port);
        this._open = true;
        resolve();
      });
    });
  }

  /**
   * Close the webHook server
   * @return {Promise} Resolves when server is closed
   */
  close() {
    if (!this.isOpen()) {
      return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
      this._webServer.close(error => {
        if (error) return reject(error);
        this._open = false;
        resolve();
      });
    });
  }

  /**
   * Check if the webhook server is open
   * @return {Boolean} True if server is listening, otherwise false
   */
  isOpen() {
    // NOTE: Since `http.Server.listening` was added in v5.7.0
    // and we still need to support Node v4,
    // we are going to fallback to 'this._open'.
    return this._open;
  }

  /**
   * Handle requests from Telegram
   * @private
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  _requestListener(req, res) {
    debug('WebHook request URL: %s', req.url);
    debug('WebHook request headers: %j', req.headers);

    // Handle bot token endpoint (update from Telegram)
    if (req.url.indexOf(this.bot.token) !== -1) {
      if (req.method !== 'POST') {
        debug('WebHook request isn\'t a POST');
        res.statusCode = 418; // I'm a teabot!
        res.end();
      } else {
        req
          .pipe(bl(this._parseBody))
          .on('finish', () => res.end('OK'));
      }
    } 
    // Handle health check endpoint
    else if (this._healthRegex.test(req.url)) {
      debug('WebHook health check passed');
      res.statusCode = 200;
      res.end('OK');
    } 
    // Handle unauthorized requests
    else {
      debug('WebHook request unauthorized');
      res.statusCode = 401;
      res.end();
    }
  }

  /**
   * Parse request body and process the update
   * @private
   * @param {Error} error - Error if any occurred during parsing
   * @param {Buffer} body - Request body
   */
  _parseBody(error, body) {
    if (error) {
      return this._error(new errors.FatalError(error));
    }

    let data;
    try {
      data = JSON.parse(body.toString());
    } catch (parseError) {
      return this._error(new errors.ParseError(parseError.message));
    }

    return this.bot.processUpdate(data);
  }

  /**
   * Handle errors during webhook processing
   * @private
   * @param {Error} error - The error that occurred
   */
  _error(error) {
    if (!this.bot.listeners('webhook_error').length) {
      return console.error('error: [webhook_error] %j', error); // eslint-disable-line no-console
    }
    return this.bot.emit('webhook_error', error);
  }
}

module.exports = TelegramBotWebHook;