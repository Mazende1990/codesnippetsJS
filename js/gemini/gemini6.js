const _ = require('lodash');
const apidoc = require('apidoc-core');
const fs = require('fs-extra');
const path = require('path');
const winston = require('winston');
const Markdown = require('markdown-it');

const PackageInfo = require('./package_info');

const defaultOptions = {
  dest: path.join(__dirname, '../doc/'),
  template: path.join(__dirname, '../template/'),
  templateSingleFile: path.join(__dirname, '../template-single/index.html'),
  debug: false,
  single: false,
  silent: false,
  verbose: false,
  simulate: false,
  parse: false,
  colorize: true,
  markdown: true,
  config: '',
  apiprivate: false,
  encoding: 'utf8',
};

const app = {
  log: {},
  markdownParser: null,
  options: {},
};

process.on('uncaughtException', (err) => {
  console.error((new Date()).toUTCString() + ' uncaughtException:', err.message);
  console.error(err.stack);
  process.exit(1);
});

/**
 * Creates the API documentation.
 *
 * @param {object} options - Configuration options. See `defaultOptions` and `apidoc-core` defaults.
 * @returns {boolean|object} - `true` if nothing to do, `false` on error, or parsed data.
 */
function createDoc(options) {
  let api;
  const apidocPath = path.join(__dirname, '../');
  let markdownParser;
  let packageInfo;

  const mergedOptions = _.defaults({}, options, defaultOptions);

  mergedOptions.dest = path.join(mergedOptions.dest, './');

  if (mergedOptions.single) {
    mergedOptions.template = mergedOptions.templateSingleFile;
    mergedOptions.dest = path.join(mergedOptions.dest, 'index.html');
  } else {
    mergedOptions.template = path.join(mergedOptions.template, './');
  }

  if (mergedOptions.lineEnding) {
    if (mergedOptions.lineEnding === 'CRLF') {
      mergedOptions.lineEnding = '\r\n';
    } else if (mergedOptions.lineEnding === 'CR') {
      mergedOptions.lineEnding = '\r';
    } else {
      mergedOptions.lineEnding = '\n';
    }
  }

  app.options = mergedOptions;

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

  if (app.options.markdown === true) {
    markdownParser = new Markdown({
      breaks: false,
      html: true,
      linkify: false,
      typographer: false,
      highlight: (str, lang) => {
        if (lang) {
          return `<pre class="prettyprint lang-<span class="math-inline">\{lang\}"\></span>{str}</pre>`;
        }
        return `<pre class="prettyprint">${str}</pre>`;
      },
    });
  } else if (app.options.markdown !== false) {
    let markdownPath = app.options.markdown;

    if (markdownPath.substr(0, 2) !== '..' && ((markdownPath.substr(0, 1) !== '/' && markdownPath.substr(1, 2) !== ':/' && markdownPath.substr(1, 2) !== ':\\' && markdownPath.substr(0, 1) !== '~') || markdownPath.substr(0, 1) === '.')) {
      markdownPath = path.join(process.cwd(), markdownPath);
    }
    Markdown = require(markdownPath);
    markdownParser = new Markdown();
  }
  app.markdownParser = markdownParser;

  try {
    packageInfo = new PackageInfo(app);

    const packageJson = JSON.parse(fs.readFileSync(apidocPath + 'package.json', 'utf8'));
    apidoc.setGeneratorInfos({
      name: packageJson.name,
      time: new Date(),
      url: packageJson.homepage,
      version: packageJson.version,
    });
    apidoc.setLogger(app.log);
    apidoc.setMarkdownParser(markdownParser);
    apidoc.setPackageInfos(packageInfo.get());

    api = apidoc.parse(app.options);

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
 * Saves parsed API data to files.
 *
 * @param {object} api - Parsed API data.
 */
function createOutputFiles(api) {
  if (app.options.simulate) {
    app.log.warn('!!! Simulation !!! No file or dir will be copied or created.');
  }

  app.log.verbose('create dir: ' + app.options.dest);
  if (!app.options.simulate) {
    fs.mkdirsSync(app.options.dest);
  }

  app.log.verbose('copy template ' + app.options.template + ' to: ' + app.options.dest);
  if (!app.options.simulate) {
    fs.copySync(app.options.template, app.options.dest);
  }

  app.log.verbose('write json file: ' + app.options.dest + 'api_data.json');
  if (!app.options.simulate) {
    fs.writeFileSync(app.options.dest + './api_data.json', api.data + '\n');
  }

  app.log.verbose('write js file: ' + app.options.dest + 'api_data.js');
  if (!app.options.simulate) {
    fs.writeFileSync(app.options.dest + './api_data.js', 'define({ "api": ' + api.data + ' });' + '\n');
  }

  app.log.verbose('write json file: ' + app.options.dest + 'api_project.json');
  if (!app.options.simulate) {
    fs.writeFileSync(app.options.dest + './api_project.json', api.project + '\n');
  }

  app.log.verbose('write js file: ' + app.options.dest + 'api_project.js');
  if (!app.options.simulate) {
    fs.writeFileSync(app.options.dest + './api_project.js', 'define(' + api.project + ');' + '\n');
  }

  app.log.verbose('write json file: ' + app.options.dest + 'api_definitions.json');
  if (!app.options.simulate && !app.options.copyDefinitions) {
    fs.writeFileSync(app.options.dest + './api_definition.json', api.definitions + '\n');
  }

  app.log.verbose('write js file: ' + app.options.dest + 'api_definitions.js');
  if (!app.options.simulate && !app.options.copyDefinitions) {
    fs.writeFileSync(app.options.dest + './api_definition.js', 'define({ "api": ' + api.definitions + ' });' + '\n');
  }
}

/**
 * Creates a single HTML file from parsed API data.
 *
 * @param {object} api - Parsed API data.
 */
function createSingleFile(api) {
  if (app.options.simulate) {
    app.log.warn('!!! Simulation !!! No file or dir will be copied or created.');
  }

  const dir = path.join(app.options.dest, '..');
  app.log.verbose('create dir: ' + dir);
  if (!app.options.simulate) {
    fs.mkdirsSync(dir);
  }
}