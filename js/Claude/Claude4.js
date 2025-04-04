/**
 * Express Route Mapper Example
 * 
 * An application that demonstrates declarative route mapping 
 * for Express applications.
 */

'use strict';

/**
 * Module dependencies.
 */
const escapeHtml = require('escape-html');
const express = require('../../lib/express');

// Configuration
const isVerboseMode = process.env.NODE_ENV !== 'test';

// Create Express application
const app = module.exports = express();

/**
 * Maps a route configuration object to Express routes.
 * 
 * @param {Object} routeConfig - Object containing route configuration
 * @param {string} [basePath=''] - Base path for the current mapping level
 */
app.map = function(routeConfig, basePath = '') {
  for (const key in routeConfig) {
    const value = routeConfig[key];
    
    switch (typeof value) {
      // Handle nested route objects: { '/path': { ... }}
      case 'object':
        app.map(value, basePath + key);
        break;
        
      // Handle route handlers: get: function(){ ... }
      case 'function':
        const fullPath = basePath;
        const method = key;
        
        if (isVerboseMode) {
          console.log('%s %s', method.toUpperCase(), fullPath);
        }
        
        app[method](fullPath, value);
        break;
    }
  }
};

/**
 * User-related route handlers
 */
const userController = {
  list: function(req, res) {
    res.send('user list');
  },

  getById: function(req, res) {
    res.send('user ' + escapeHtml(req.params.uid));
  },

  deleteAll: function(req, res) {
    res.send('delete users');
  }
};

/**
 * Pet-related route handlers
 */
const petController = {
  listByUser: function(req, res) {
    res.send('user ' + escapeHtml(req.params.uid) + '\'s pets');
  },

  deleteByUserAndId: function(req, res) {
    res.send(
      'delete ' + escapeHtml(req.params.uid) + 
      '\'s pet ' + escapeHtml(req.params.pid)
    );
  }
};

// Define the application routes
app.map({
  '/users': {
    get: userController.list,
    delete: userController.deleteAll,
    '/:uid': {
      get: userController.getById,
      '/pets': {
        get: petController.listByUser,
        '/:pid': {
          delete: petController.deleteByUserAndId
        }
      }
    }
  }
});

/**
 * Start the server if this module is run directly
 */
/* istanbul ignore next */
if (!module.parent) {
  const PORT = 3000;
  app.listen(PORT);
  console.log(`Express started on port ${PORT}`);
}