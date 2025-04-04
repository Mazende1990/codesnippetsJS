const errors = require('./errors');
const debug = require('debug')('node-telegram-bot-api');
const https = require('https');
const http = require('http');
const fs = require('fs');
const bl = require('bl');
const Promise = require('bluebird');

class TelegramBotWebHook {
  /**
   * Sets up a webhook to receive updates.
   * @param {TelegramBot} bot - The Telegram bot instance.
   * @see https://core.telegram.org/bots/api#getting-updates
   */
  constructor(bot) {
    this.bot = bot;
    this.options = typeof bot.options.webHook === 'boolean' ? {} : bot.options.webHook;
    this._initializeOptions();
    this._initializeWebServer();
    this._bindMethods();
  }

  /**
   * Initialize default options.
   * @private
   */
  _initializeOptions() {
    this.options.host = this.options.host || '0.0.0.0';
    this.options.port = this.options.port || 8443;
    this.options.https = this.options.https || {};
    this.options.healthEndpoint = this.options.healthEndpoint || '/healthz';
    this._healthRegex = new RegExp(this.options.healthEndpoint);
    this._open = false;
  }

  /**
   * Bind class methods to the instance.
   * @private
   */
  _bindMethods() {
    this._requestListener = this._requestListener.bind(this);
    this._parseBody = this._parseBody.bind(this);
  }

  /**
   * Initialize the web server based on the provided options.
   * @private
   */
  _initializeWebServer() {
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
      debug('HTTPS WebHook enabled (by https)');
      this._webServer = https.createServer(this.options.https, this._requestListener);
    } else {
      debug('HTTP WebHook enabled');
      this._webServer = http.createServer(this._requestListener);
    }
  }

  /**
   * Open the WebHook by listening on the specified port.
   * @return {Promise}
   */
  open() {
    if (this.isOpen()) {
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      this._webServer.listen(this.options.port, this.options.host, () => {
        debug('WebHook listening on port %s', this.options.port);
        this._open = true;
        resolve();
      });
    });
  }

  /**
   * Close the WebHook server.
   * @return {Promise}
   */
  close() {
    if (!this.isOpen()) {
      return Promise.resolve();
    }
    return new Promise((resolve, reject) => {
      this._webServer.close((error) => {
        if (error) {
          reject(error);
        } else {
          this._open = false;
          resolve();
        }
      });
    });
  }

  /**
   * Check if the server is currently listening.
   * @return {boolean}
   */
  isOpen() {
    return this._open;
  }

  /**
   * Handle errors during webhook request processing.
   * @private
   * @param {Error} error - The error to handle.
   */
  _error(error) {
    if (!this.bot.listeners('webhook_error').length) {
      console.error('error: [webhook_error] %j', error); // eslint-disable-line no-console
    } else {
      this.bot.emit('webhook_error', error);
    }
  }

  /**
   * Parse the request body and process the update.
   * @private
   * @param {Error} error - The error, if any.
   * @param {Buffer} body - The request body.
   */
  _parseBody(error, body) {
    if (error) {
      return this._error(new errors.FatalError(error));
    }

    try {
      const data = JSON.parse(body.toString());
      this.bot.processUpdate(data);
    } catch (parseError) {
      this._error(new errors.ParseError(parseError.message));
    }
  }

  /**
   * Handle incoming HTTP requests.
   * @private
   * @param {http.IncomingMessage} req - The HTTP request.
   * @param {http.ServerResponse} res - The HTTP response.
   */
  _requestListener(req, res) {
    debug('WebHook request URL: %s', req.url);
    debug('WebHook request headers: %j', req.headers);

    if (req.url.includes(this.bot.token)) {
      if (req.method !== 'POST') {
        debug('WebHook request is not a POST');
        res.statusCode = 418; // I'm a teapot!
        res.end();
      } else {
        req.pipe(bl(this._parseBody)).on('finish', () => res.end('OK'));
      }
    } else if (this._healthRegex.test(req.url)) {
      debug('WebHook health check passed');
      res.statusCode = 200;
      res.end('OK');
    } else {
      debug('WebHook request unauthorized');
      res.statusCode = 401;
      res.end();
    }
  }
}

module.exports = TelegramBotWebHook;