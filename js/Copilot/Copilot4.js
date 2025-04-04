/**
 * Module dependencies.
 */
const escapeHtml = require('escape-html');
const express = require('../../lib/express');

const verbose = process.env.NODE_ENV !== 'test';

const app = module.exports = express();

app.map = function(routes, baseRoute = '') {
  Object.entries(routes).forEach(([key, value]) => {
    const route = `${baseRoute}${key}`;
    if (typeof value === 'object') {
      app.map(value, route);
    } else if (typeof value === 'function') {
      if (verbose) console.log('%s %s', key, route);
      appkey;
    }
  });
};

const users = {
  list(req, res) {
    res.send('user list');
  },

  get(req, res) {
    res.send(`user ${escapeHtml(req.params.uid)}`);
  },

  delete(req, res) {
    res.send('delete users');
  }
};

const pets = {
  list(req, res) {
    res.send(`user ${escapeHtml(req.params.uid)}'s pets`);
  },

  delete(req, res) {
    res.send(`delete ${escapeHtml(req.params.uid)}'s pet ${escapeHtml(req.params.pid)}`);
  }
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
          delete: pets.delete
        }
      }
    }
  }
});

/* istanbul ignore next */
if (!module.parent) {
  app.listen(3000);
  console.log('Express started on port 3000');
}