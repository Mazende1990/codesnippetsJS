/**
 * Module dependencies.
 */

const escapeHtml = require('escape-html');
const express = require('../../lib/express');

const verbose = process.env.NODE_ENV !== 'test';

const app = (module.exports = express());

/**
 * Maps route definitions to Express routes.
 *
 * @param {object} routes - An object defining route paths and handlers.
 * @param {string} [route=''] - The base route path.
 */
app.map = function (routes, route = '') {
  for (const key in routes) {
    if (Object.prototype.hasOwnProperty.call(routes, key)) {
      const value = routes[key];
      switch (typeof value) {
        // { '/path': { ... }}
        case 'object':
          this.map(value, route + key);
          break;
        // get: function(){ ... }
        case 'function':
          if (verbose) console.log('%s %s', key, route);
          this[key](route, value);
          break;
        default:
          break;
      }
    }
  }
};

const users = {
  list: function (req, res) {
    res.send('user list');
  },

  get: function (req, res) {
    res.send('user ' + escapeHtml(req.params.uid));
  },

  delete: function (req, res) {
    res.send('delete users');
  },
};

const pets = {
  list: function (req, res) {
    res.send("user " + escapeHtml(req.params.uid) + "'s pets");
  },

  delete: function (req, res) {
    res.send("delete " + escapeHtml(req.params.uid) + "'s pet " + escapeHtml(req.params.pid));
  },
};

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
if (!module.parent) {
  app.listen(3000);
  console.log('Express started on port 3000');
}