/**
 * Module dependencies.
 */
const escapeHtml = require('escape-html');
const express = require('../../lib/express');

// Enable verbose logging unless in test environment
const verbose = process.env.NODE_ENV !== 'test';

// Create an Express application
const app = module.exports = express();

/**
 * Recursively maps routes to their corresponding handlers.
 * @param {Object} routes - The routes configuration object.
 * @param {string} baseRoute - The base route path (used for recursion).
 */
app.map = function(routes, baseRoute = '') {
  for (const [path, handler] of Object.entries(routes)) {
    if (typeof handler === 'object') {
      // If the handler is an object, recursively map its routes
      app.map(handler, `${baseRoute}${path}`);
    } else if (typeof handler === 'function') {
      // If the handler is a function, register it as a route handler
      if (verbose) console.log('%s %s', path, baseRoute);
      app[path](baseRoute, handler);
    }
  }
};

// Define user-related route handlers
const users = {
  list: (req, res) => {
    res.send('user list');
  },

  get: (req, res) => {
    res.send(`user ${escapeHtml(req.params.uid)}`);
  },

  delete: (req, res) => {
    res.send('delete users');
  },
};

// Define pet-related route handlers
const pets = {
  list: (req, res) => {
    res.send(`user ${escapeHtml(req.params.uid)}'s pets`);
  },

  delete: (req, res) => {
    res.send(`delete ${escapeHtml(req.params.uid)}'s pet ${escapeHtml(req.params.pid)}`);
  },
};

// Configure routes using the app.map function
app.map({
  '/users': {
    get: users.list,
    delete: users.delete,
    '/:uid': {
      get: users.get,
      '/pets': {
        get: pets.list,
        '/:pid': {
          delete: pets.delete,
        },
      },
    },
  },
});

/* istanbul ignore next */
// Start the server if this file is run directly
if (!module.parent) {
  app.listen(3000);
  console.log('Express started on port 3000');
}