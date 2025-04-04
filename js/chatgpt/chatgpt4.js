/**
 * Module dependencies.
 */
const escapeHtml = require('escape-html');
const express = require('../../lib/express');

const verbose = process.env.NODE_ENV !== 'test';

const app = express();

/**
 * Recursively maps route definitions to Express app.
 *
 * @param {Object} routes - The route definitions.
 * @param {string} basePath - The current base route.
 */
const mapRoutes = (routes, basePath = '') => {
  Object.entries(routes).forEach(([path, handler]) => {
    const fullPath = `${basePath}${path}`;

    if (typeof handler === 'object') {
      // Recursively map nested routes
      mapRoutes(handler, fullPath);
    } else if (typeof handler === 'function') {
      if (verbose) console.log(`${path.toUpperCase()} ${fullPath}`);
      app[path](fullPath, handler);
    }
  });
};

// Define API route handlers
const routes = {
  '/users': {
    get: (req, res) => res.send('user list'),
    delete: (req, res) => res.send('delete users'),
    '/:uid': {
      get: (req, res) => res.send(`user ${escapeHtml(req.params.uid)}`),
      '/pets': {
        get: (req, res) => res.send(`user ${escapeHtml(req.params.uid)}'s pets`),
        '/:pid': {
          delete: (req, res) =>
            res.send(`delete ${escapeHtml(req.params.uid)}'s pet ${escapeHtml(req.params.pid)}`)
        }
      }
    }
  }
};

// Map defined routes
mapRoutes(routes);

/* istanbul ignore next */
if (!module.parent) {
  app.listen(3000, () => console.log('Express started on port 3000'));
}

module.exports = app;
