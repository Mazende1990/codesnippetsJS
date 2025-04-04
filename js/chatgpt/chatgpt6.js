const _ = require('lodash');
const apidoc = require('apidoc-core');
const fs = require('fs-extra');
const path = require('path');
const winston = require('winston');
const Markdown = require('markdown-it');

const PackageInfo = require('./package_info');

const defaults = {
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

// Handle uncaught exceptions globally
process.on('uncaughtException', (err) => {
    console.error(`${new Date().toUTCString()} uncaughtException:`, err.message);
    console.error(err.stack);
    process.exit(1);
});

/**
 * Initializes logging based on app options.
 */
const setupLogger = () => {
    return winston.createLogger({
        transports: [
            new winston.transports.Console({
                level: app.options.debug ? 'debug' : app.options.verbose ? 'verbose' : 'info',
                silent: app.options.silent,
                format: winston.format.simple(),
            }),
        ],
    });
};

/**
 * Initializes the Markdown parser based on the provided options.
 * @returns {Markdown}
 */
const setupMarkdownParser = () => {
    if (app.options.markdown === true) {
        return new Markdown({
            breaks: false,
            html: true,
            linkify: false,
            typographer: false,
            highlight: (str, lang) =>
                lang
                    ? `<pre class="prettyprint lang-${lang}">${str}</pre>`
                    : `<pre class="prettyprint">${str}</pre>`,
        });
    } else if (app.options.markdown) {
        const markdownPath = path.isAbsolute(app.options.markdown)
            ? app.options.markdown
            : path.join(process.cwd(), app.options.markdown);
        return new (require(markdownPath))();
    }
    return null;
};

/**
 * Creates a directory if it doesn't exist.
 * @param {string} dirPath
 */
const createDirectory = (dirPath) => {
    if (!app.options.simulate) {
        fs.mkdirsSync(dirPath);
    }
};

/**
 * Writes data to a file if simulation mode is not enabled.
 * @param {string} filePath
 * @param {string} data
 */
const writeFile = (filePath, data) => {
    if (!app.options.simulate) {
        fs.writeFileSync(filePath, data);
    }
};

/**
 * Copies the template to the destination if simulation mode is not enabled.
 * @param {string} source
 * @param {string} destination
 */
const copyTemplate = (source, destination) => {
    if (!app.options.simulate) {
        fs.copySync(source, destination);
    }
};

/**
 * Generates the API documentation.
 * @param {Object} options
 * @returns {boolean|Object} true if nothing to do, false if error, or API data object.
 */
const createDoc = (options) => {
    try {
        options = _.defaults({}, options, defaults);
        app.options = options;
        app.log = setupLogger();
        app.markdownParser = setupMarkdownParser();

        const apidocPath = path.join(__dirname, '../');
        const packageInfo = new PackageInfo(app);

        if (options.single) {
            options.template = options.templateSingleFile;
            options.dest = path.join(options.dest, 'index.html');
        } else {
            options.template = path.join(options.template, './');
        }

        // Set line endings
        if (options.lineEnding) {
            options.lineEnding = options.lineEnding === 'CRLF' ? '\r\n' : options.lineEnding === 'CR' ? '\r' : '\n';
        }

        // Set up apidoc generator
        const json = JSON.parse(fs.readFileSync(apidocPath + 'package.json', 'utf8'));
        apidoc.setGeneratorInfos({
            name: json.name,
            time: new Date(),
            url: json.homepage,
            version: json.version,
        });

        apidoc.setLogger(app.log);
        apidoc.setMarkdownParser(app.markdownParser);
        apidoc.setPackageInfos(packageInfo.get());

        const api = apidoc.parse(app.options);

        if (api === true) {
            app.log.info('Nothing to do.');
            return true;
        }
        if (api === false) return false;

        if (!app.options.parse) {
            app.options.single ? createSingleFile(api) : createOutputFiles(api);
        }

        if (app.options.verbose) {
            app.log.info('Done.');
        }

        return api;
    } catch (error) {
        app.log.error(error.message);
        app.log.debug(error.stack);
        return false;
    }
};

/**
 * Saves parsed data to files.
 * @param {Object} api
 */
const createOutputFiles = (api) => {
    createDirectory(app.options.dest);
    copyTemplate(app.options.template, app.options.dest);

    const files = {
        'api_data.json': api.data,
        'api_data.js': `define({ "api": ${api.data} });\n`,
        'api_project.json': api.project,
        'api_project.js': `define(${api.project});\n`,
    };

    if (!app.options.copyDefinitions) {
        files['api_definitions.json'] = api.definitions;
        files['api_definitions.js'] = `define({ "api": ${api.definitions} });\n`;
    }

    Object.entries(files).forEach(([fileName, content]) => {
        app.log.verbose(`Writing file: ${app.options.dest + fileName}`);
        writeFile(path.join(app.options.dest, fileName), content);
    });
};

/**
 * Generates a single file containing the API documentation.
 * @param {Object} api
 */
const createSingleFile = (api) => {
    const dir = path.join(app.options.dest, '..');
    createDirectory(dir);

    const templateContent = fs.readFileSync(app.options.template).toString();
    const finalContent = templateContent
        .replace('__API_DATA__', api.data)
        .replace('__API_PROJECT__', api.project);

    writeFile(app.options.dest, finalContent);
};

module.exports = { createDoc };
