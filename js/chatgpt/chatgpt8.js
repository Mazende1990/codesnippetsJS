const errors = require('./errors');
const debug = require('debug')('node-telegram-bot-api');
const https = require('https');
const http = require('http');
const fs = require('fs');
const bl = require('bl');
const Promise = require('bluebird');

class TelegramBotWebHook {
  /**
   * Sets up a webhook to receive updates
   * @param  {TelegramBot} bot
   * @see https://core.telegram.org/bots/api#getting-updates
   */
  constructor(bot) {
    this.bot = bot;
    this.options = typeof bot.options.webHook === 'boolean' ? {} : bot.options.webHook;

    // Default webhook options
    this.options = {
      host: this.options.host || '0.0.0.0',
      port: this.options.port || 8443,
      https: this.options.https || {},
      healthEndpoint: this.options.healthEndpoint || '/healthz',
      ...this.options,
    };

    this._healthRegex = new RegExp(this.options.healthEndpoint);
    this._open = false;

    this._requestListener = this._requestListener.bind(this);
    this._parseBody = this._parseBody.bind(this);

    // Initialize the web server
    this._webServer = this._createWebServer();
  }

  /**
   * Creates an HTTP or HTTPS server based on the provided options.
   * @private
   */
  _createWebServer() {
    const { key, cert, pfx, https: httpsOptions } = this.options;

    if (key && cert) {
      debug('HTTPS WebHook enabled (by key/cert)');
      return https.createServer(
        { key: fs.readFileSync(key), cert: fs.readFileSync(cert) },
        this._requestListener
      );
    }

    if (pfx) {
      debug('HTTPS WebHook enabled (by pfx)');
      return https.createServer(
        { pfx: fs.readFileSync(pfx) },
        this._requestListener
      );
    }

    if (Object.keys(httpsOptions).length) {
      debug('HTTPS WebHook enabled by (https options)');
      return https.createServer(httpsOptions, this._requestListener);
    }

    debug('HTTP WebHook enabled');
    return http.createServer(this._requestListener);
  }

  /**
   * Opens the webhook by starting the server.
   * @returns {Promise}
   */
  open() {
    if (this.isOpen()) return Promise.resolve();

    return new Promise((resolve) => {
      this._webServer.listen(this.options.port, this.options.host, () => {
        debug('WebHook listening on port %s', this.options.port);
        this._open = true;
        resolve();
      });
    });
  }

  /**
   * Closes the webhook server.
   * @returns {Promise}
   */
  close() {
    if (!this.isOpen()) return Promise.resolve();

    return new Promise((resolve, reject) => {
      this._webServer.close((error) => {
        if (error) return reject(error);
        this._open = false;
        resolve();
      });
    });
  }

  /**
   * Checks if the webhook is currently open.
   * @returns {boolean}
   */
  isOpen() {
    return this._open;
  }

  /**
   * Handles errors encountered during request processing.
   * @private
   * @param {Error} error
   */
  _handleError(error) {
    if (!this.bot.listeners('webhook_error').length) {
      console.error('error: [webhook_error] %j', error); // eslint-disable-line no-console
    } else {
      this.bot.emit('webhook_error', error);
    }
  }

  /**
   * Parses the request body and processes the update.
   * @private
   */
  _parseBody(error, body) {
    if (error) return this._handleError(new errors.FatalError(error));

    try {
      const data = JSON.parse(body.toString());
      return this.bot.processUpdate(data);
    } catch (parseError) {
      return this._handleError(new errors.ParseError(parseError.message));
    }
  }

  /**
   * Handles incoming webhook requests.
   * @private
   */
  _requestListener(req, res) {
    debug('WebHook request URL: %s', req.url);
    debug('WebHook request headers: %j', req.headers);

    if (req.url.includes(this.bot.token)) {
      return this._handleWebhookRequest(req, res);
    }

    if (this._healthRegex.test(req.url)) {
      return this._handleHealthCheck(res);
    }

    return this._handleUnauthorizedRequest(res);
  }

  /**
   * Handles webhook requests.
   * @private
   */
  _handleWebhookRequest(req, res) {
    if (req.method !== 'POST') {
      debug('WebHook request isn\'t a POST');
      res.statusCode = 418; // I'm a teabot!
      return res.end();
    }

    req.pipe(bl(this._parseBody)).on('finish', () => res.end('OK'));
  }

  /**
   * Handles health check requests.
   * @private
   */
  _handleHealthCheck(res) {
    debug('WebHook health check passed');
    res.statusCode = 200;
    res.end('OK');
  }

  /**
   * Handles unauthorized requests.
   * @private
   */
  _handleUnauthorizedRequest(res) {
    debug('WebHook request unauthorized');
    res.statusCode = 401;
    res.end();
  }
}

module.exports = TelegramBotWebHook;
