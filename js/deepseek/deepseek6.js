const _ = require('lodash');
const apidoc = require('apidoc-core');
const fs = require('fs-extra');
const path = require('path');
const winston = require('winston');
const Markdown = require('markdown-it');
const PackageInfo = require('./package_info');

// Default configuration options
const defaults = {
  dest: path.join(__dirname, '../doc/'),
  template: path.join(__dirname, '../template/'),
  templateSingleFile: path.join(__dirname, '../template-single/index.html'),
  debug: false,
  single: false, // Build to a single file
  silent: false,
  verbose: false,
  simulate: false,
  parse: false, // Only parse and return the data, no file creation
  colorize: true,
  markdown: true,
  config: '',
  apiprivate: false,
  encoding: 'utf8',
};

// Application context
const app = {
  log: {},
  markdownParser: null,
  options: {},
};

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error(`${new Date().toUTCString()} uncaughtException: ${err.message}`);
  console.error(err.stack);
  process.exit(1);
});

/**
 * Initialize the logger with the given options.
 */
function initializeLogger() {
  app.log = winston.createLogger({
    transports: [
      new winston.transports.Console({
        level: app.options.debug ? 'debug' : app.options.verbose ? 'verbose' : 'info',
        silent: app.options.silent,
        prettyPrint: true,
        colorize: app.options.colorize,
        timestamp: false,
      }),
    ],
  });
}

/**
 * Initialize the Markdown parser based on the provided options.
 */
function initializeMarkdownParser() {
  if (app.options.markdown === true) {
    app.markdownParser = new Markdown({
      breaks: false,
      html: true,
      linkify: false,
      typographer: false,
      highlight: (str, lang) => {
        if (lang) {
          return `<pre class="prettyprint lang-${lang}">${str}</pre>`;
        }
        return `<pre class="prettyprint">${str}</code></pre>`;
      },
    });
  } else if (typeof app.options.markdown === 'string') {
    // Load a custom Markdown parser
    const markdownPath = path.resolve(app.options.markdown);
    const CustomMarkdown = require(markdownPath);
    app.markdownParser = new CustomMarkdown();
  }
}

/**
 * Normalize paths and set up options.
 */
function setupOptions(options) {
  app.options = _.defaults({}, options, defaults);

  // Normalize paths
  app.options.dest = path.join(app.options.dest, './');
  app.options.template = app.options.single
    ? app.options.templateSingleFile
    : path.join(app.options.template, './');
}

/**
 * Set up apidoc generator information.
 */
function setupApidocGenerator() {
  const apidocPath = path.join(__dirname, '../');
  const packageJson = JSON.parse(fs.readFileSync(path.join(apidocPath, 'package.json'), 'utf8');

  apidoc.setGeneratorInfos({
    name: packageJson.name,
    time: new Date(),
    url: packageJson.homepage,
    version: packageJson.version,
  });
  apidoc.setLogger(app.log);
  apidoc.setMarkdownParser(app.markdownParser);
  apidoc.setPackageInfos(new PackageInfo(app).get());
}

/**
 * Create the documentation.
 * @param {Object} options - Configuration options.
 * @returns {Mixed} - Returns `true` if nothing to do, `false` on error, or the parsed API data.
 */
function createDoc(options) {
  setupOptions(options);
  initializeLogger();
  initializeMarkdownParser();

  try {
    setupApidocGenerator();
    const api = apidoc.parse(app.options);

    if (api === true) {
      app.log.info('Nothing to do.');
      return true;
    }
    if (api === false) {
      return false;
    }

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
  } catch (e) {
    app.log.error(e.message);
    if (e.stack) {
      app.log.debug(e.stack);
    }
    return false;
  }
}

/**
 * Save parsed data to multiple output files.
 * @param {Object} api - The parsed API data.
 */
function createOutputFiles(api) {
  if (app.options.simulate) {
    app.log.warn('!!! Simulation !!! No file or dir will be copied or created.');
  }

  app.log.verbose(`Create dir: ${app.options.dest}`);
  if (!app.options.simulate) {
    fs.mkdirsSync(app.options.dest);
  }

  app.log.verbose(`Copy template ${app.options.template} to: ${app.options.dest}`);
  if (!app.options.simulate) {
    fs.copySync(app.options.template, app.options.dest);
  }

  // Write API data files
  writeFileSyncSafe(`${app.options.dest}api_data.json`, api.data + '\n');
  writeFileSyncSafe(`${app.options.dest}api_data.js`, `define({ "api": ${api.data} });\n`);

  // Write API project files
  writeFileSyncSafe(`${app.options.dest}api_project.json`, api.project + '\n');
  writeFileSyncSafe(`${app.options.dest}api_project.js`, `define(${api.project});\n`);

  // Write API definitions files
  if (!app.options.copyDefinitions) {
    writeFileSyncSafe(`${app.options.dest}api_definitions.json`, api.definitions + '\n');
    writeFileSyncSafe(`${app.options.dest}api_definitions.js`, `define({ "api": ${api.definitions} });\n`);
  }
}

/**
 * Save parsed data to a single output file.
 * @param {Object} api - The parsed API data.
 */
function createSingleFile(api) {
  if (app.options.simulate) {
    app.log.warn('!!! Simulation !!! No file or dir will be copied or created.');
  }

  const dir = path.join(app.options.dest, '..');
  app.log.verbose(`Create dir: ${dir}`);
  if (!app.options.simulate) {
    fs.mkdirsSync(dir);
  }

  app.log.verbose(`Generate file: ${app.options.dest}`);
  const templateContent = fs.readFileSync(app.options.template).toString();
  const finalContent = templateContent
    .replace('__API_DATA__', api.data)
    .replace('__API_PROJECT__', api.project);

  if (!app.options.simulate) {
    fs.writeFileSync(app.options.dest, finalContent);
  }
}

/**
 * Safely write a file with logging.
 * @param {string} filePath - The path to the file.
 * @param {string} content - The content to write.
 */
function writeFileSyncSafe(filePath, content) {
  app.log.verbose(`Write file: ${filePath}`);
  if (!app.options.simulate) {
    fs.writeFileSync(filePath, content);
  }
}

module.exports = {
  createDoc,
};