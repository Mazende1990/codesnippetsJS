/**
 * APIDoc Documentation Generator
 * 
 * Creates API documentation from source code comments.
 */

'use strict';

// Dependencies
const _           = require('lodash');
const apidoc      = require('apidoc-core');
const fs          = require('fs-extra');
const path        = require('path');
const winston     = require('winston');
const Markdown    = require('markdown-it');
const PackageInfo = require('./package_info');

// Default configuration
const DEFAULT_CONFIG = {
  dest                : path.join(__dirname, '../doc/'),
  template            : path.join(__dirname, '../template/'),
  templateSingleFile  : path.join(__dirname, '../template-single/index.html'),
  debug               : false,
  single              : false, // build to single file
  silent              : false,
  verbose             : false,
  simulate            : false,
  parse               : false, // Only parse and return the data, no file creation
  colorize            : true,
  markdown            : true,
  config              : '',
  apiprivate          : false,
  encoding            : 'utf8'
};

// Application state
const app = {
  log             : {},
  markdownParser  : null,
  options         : {}
};

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error(`${new Date().toUTCString()} uncaughtException: ${err.message}`);
  console.error(err.stack);
  process.exit(1);
});

/**
 * Creates a markdown parser instance based on configuration
 * 
 * @param {Object} options - Configuration options
 * @returns {Object|null} - Markdown parser instance or null if disabled
 */
function createMarkdownParser(options) {
  // Markdown is disabled
  if (options.markdown === false) {
    return null;
  }
  
  // Use default markdown parser
  if (options.markdown === true) {
    return new Markdown({
      breaks      : false,
      html        : true,
      linkify     : false,
      typographer : false,
      highlight   : function(str, lang) {
        if (lang) {
          return `<pre class="prettyprint lang-${lang}">${str}</pre>`;
        }
        return '<pre class="prettyprint">' + str + '</code></pre>';
      }
    });
  }
  
  // Use custom markdown parser
  let customParserPath = options.markdown;
  
  // Resolve relative path
  if (shouldResolveRelativePath(customParserPath)) {
    customParserPath = path.join(process.cwd(), customParserPath);
  }
  
  // Load custom parser
  const CustomMarkdown = require(customParserPath);
  return new CustomMarkdown();
}

/**
 * Checks if a path should be resolved relative to CWD
 * 
 * @param {string} filePath - Path to check
 * @returns {boolean} - True if path should be resolved
 */
function shouldResolveRelativePath(filePath) {
  const isRelative = filePath.startsWith('.');
  const isAbsolute = 
    filePath.startsWith('/') || 
    filePath.substr(1, 2) === ':/' || 
    filePath.substr(1, 2) === ':\\' || 
    filePath.startsWith('~');
  
  return (isRelative || !isAbsolute) && filePath.substr(0, 2) !== '..';
}

/**
 * Configures the line ending based on user preferences
 * 
 * @param {Object} options - Configuration options
 * @returns {Object} - Updated options
 */
function configureLineEnding(options) {
  if (options.lineEnding) {
    if (options.lineEnding === 'CRLF') {
      options.lineEnding = '\r\n'; // win32
    } else if (options.lineEnding === 'CR') {
      options.lineEnding = '\r'; // darwin
    } else {
      options.lineEnding = '\n'; // linux
    }
  }
  return options;
}

/**
 * Configures the logger based on user preferences
 * 
 * @param {Object} options - Configuration options
 * @returns {Object} - Winston logger instance
 */
function configureLogger(options) {
  const logLevel = options.debug ? 'debug' : (options.verbose ? 'verbose' : 'info');
  
  return winston.createLogger({
    transports: [
      new winston.transports.Console({
        level       : logLevel,
        silent      : options.silent,
        prettyPrint : true,
        colorize    : options.colorize,
        timestamp   : false
      }),
    ]
  });
}

/**
 * Create the documentation
 *
 * @param {Object} options - See DEFAULT_CONFIG and apidoc-core defaults for all options / `apidoc --help`
 * @returns {Mixed} true = ok, but nothing to do | false = error | Object with parsed data and project information
 */
function createDoc(options) {
  try {
    // Merge options with defaults
    options = _.defaults({}, options, DEFAULT_CONFIG);
    
    // Configure paths
    options.dest = path.join(options.dest, './');
    
    if (options.single) {
      options.template = options.templateSingleFile;
      options.dest = path.join(options.dest, 'index.html');
    } else {
      options.template = path.join(options.template, './');
    }
    
    // Configure line endings
    options = configureLineEnding(options);
    
    // Set application options
    app.options = options;
    
    // Setup logger
    app.log = configureLogger(options);
    
    // Setup markdown parser
    app.markdownParser = createMarkdownParser(options);
    
    // Initialize package info
    const packageInfo = new PackageInfo(app);
    
    // Configure apidoc-core
    const apidocPath = path.join(__dirname, '../');
    const generatorInfo = JSON.parse(fs.readFileSync(path.join(apidocPath, 'package.json'), 'utf8'));
    
    apidoc.setGeneratorInfos({
      name    : generatorInfo.name,
      time    : new Date(),
      url     : generatorInfo.homepage,
      version : generatorInfo.version
    });
    
    apidoc.setLogger(app.log);
    apidoc.setMarkdownParser(app.markdownParser);
    apidoc.setPackageInfos(packageInfo.get());
    
    // Parse the source files
    const api = apidoc.parse(app.options);
    
    // Handle parsing results
    if (api === true) {
      app.log.info('Nothing to do.');
      return true;
    }
    
    if (api === false) {
      return false;
    }
    
    // Generate output if not in parse-only mode
    if (app.options.parse !== true) {
      if (app.options.single) {
        createSingleFile(api);
      } else {
        createOutputFiles(api);
      }
    }
    
    if (app.options.verbose) {
      app.log.info('Done.');
    }
    
    return api;
  } catch (error) {
    app.log.error(error.message);
    if (error.stack) {
      app.log.debug(error.stack);
    }
    return false;
  }
}

/**
 * Save parsed data to multiple files
 *
 * @param {Object} api - Parsed API data
 */
function createOutputFiles(api) {
  if (app.options.simulate) {
    app.log.warn('!!! Simulation !!! No file or directory will be copied or created.');
  }
  
  // Create output directory
  app.log.verbose('Create directory: ' + app.options.dest);
  if (!app.options.simulate) {
    fs.mkdirsSync(app.options.dest);
  }
  
  // Copy template files
  app.log.verbose('Copy template from ' + app.options.template + ' to: ' + app.options.dest);
  if (!app.options.simulate) {
    fs.copySync(app.options.template, app.options.dest);
  }
  
  const destPath = app.options.dest;
  
  // Write API data files
  const files = [
    { 
      path: path.join(destPath, 'api_data.json'),
      content: api.data + '\n',
      type: 'json'
    },
    { 
      path: path.join(destPath, 'api_data.js'),
      content: 'define({ "api": ' + api.data + ' });' + '\n',
      type: 'js'
    },
    { 
      path: path.join(destPath, 'api_project.json'),
      content: api.project + '\n',
      type: 'json'
    },
    { 
      path: path.join(destPath, 'api_project.js'),
      content: 'define(' + api.project + ');' + '\n',
      type: 'js'
    }
  ];
  
  // Add definition files if needed
  if (!app.options.copyDefinitions) {
    files.push({
      path: path.join(destPath, 'api_definition.json'),
      content: api.definitions + '\n',
      type: 'json'
    });
    files.push({
      path: path.join(destPath, 'api_definition.js'),
      content: 'define({ "api": ' + api.definitions + ' });' + '\n',
      type: 'js'
    });
  }
  
  // Write all files
  files.forEach(file => {
    app.log.verbose(`Write ${file.type} file: ${file.path}`);
    if (!app.options.simulate) {
      fs.writeFileSync(file.path, file.content);
    }
  });
}

/**
 * Creates a single HTML file with embedded API data
 *
 * @param {Object} api - Parsed API data
 */
function createSingleFile(api) {
  if (app.options.simulate) {
    app.log.warn('!!! Simulation !!! No file or directory will be copied or created.');
  }
  
  // Create target directory if needed
  const targetDir = path.join(app.options.dest, '..');
  app.log.verbose('Create directory: ' + targetDir);
  
  if (!app.options.simulate) {
    fs.mkdirsSync(targetDir);
  }
  
  // Create output file with embedded data
  app.log.verbose('Generate file: ' + app.options.dest);
  
  if (!app.options.simulate) {
    const template = fs.readFileSync(app.options.template).toString();
    const content = template
      .replace('__API_DATA__', api.data)
      .replace('__API_PROJECT__', api.project);
      
    fs.writeFileSync(app.options.dest, content);
  }
}

// Exports
module.exports = {
  createDoc
};