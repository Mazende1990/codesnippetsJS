import assign from './assign.mjs';
import defaultConverter from './converter.mjs';

/**
 * Initialize the cookie utility with a custom converter and default attributes.
 * @param {Object} converter - The converter for reading/writing cookie values.
 * @param {Object} defaultAttributes - Default attributes for cookies (e.g., path, expires).
 * @returns {Object} - An object with methods to interact with cookies.
 */
function init(converter, defaultAttributes) {
  /**
   * Set a cookie with the given key, value, and attributes.
   * @param {string} key - The cookie key.
   * @param {string} value - The cookie value.
   * @param {Object} attributes - Additional cookie attributes (e.g., expires, path).
   * @returns {string} - The updated cookie string.
   */
  function set(key, value, attributes) {
    if (typeof document === 'undefined') {
      return;
    }

    // Merge default attributes with provided attributes
    attributes = assign({}, defaultAttributes, attributes);

    // Convert expires to a UTC string if it's a number or Date
    if (typeof attributes.expires === 'number') {
      attributes.expires = new Date(Date.now() + attributes.expires * 864e5);
    }
    if (attributes.expires) {
      attributes.expires = attributes.expires.toUTCString();
    }

    // Encode the key and handle special characters
    key = encodeURIComponent(key)
      .replace(/%(2[346B]|5E|60|7C)/g, decodeURIComponent)
      .replace(/[()]/g, escape);

    // Convert the value using the provided converter
    value = converter.write(value, key);

    // Build the cookie attributes string
    let stringifiedAttributes = '';
    for (const attributeName in attributes) {
      if (!attributes[attributeName]) {
        continue;
      }

      stringifiedAttributes += `; ${attributeName}`;

      if (attributes[attributeName] === true) {
        continue;
      }

      // Handle attributes with values (e.g., expires, path)
      stringifiedAttributes += `=${attributes[attributeName].split(';')[0]}`;
    }

    // Set the cookie
    return (document.cookie = `${key}=${value}${stringifiedAttributes}`);
  }

  /**
   * Get the value of a cookie by its key.
   * @param {string} key - The cookie key.
   * @returns {string|Object} - The cookie value or an object of all cookies.
   */
  function get(key) {
    if (typeof document === 'undefined' || (arguments.length && !key)) {
      return;
    }

    // Split document.cookie into individual cookies
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    const jar = {};

    for (const cookie of cookies) {
      const [cookieKey, ...cookieValueParts] = cookie.split('=');
      let value = cookieValueParts.join('=');

      // Remove surrounding quotes if present
      if (value[0] === '"') {
        value = value.slice(1, -1);
      }

      try {
        const foundKey = defaultConverter.read(cookieKey);
        jar[foundKey] = converter.read(value, foundKey);

        // Stop searching if the target key is found
        if (key === foundKey) {
          break;
        }
      } catch (e) {
        // Ignore invalid cookies
      }
    }

    return key ? jar[key] : jar;
  }

  /**
   * Remove a cookie by setting its expiration to the past.
   * @param {string} key - The cookie key.
   * @param {Object} attributes - Additional attributes for the cookie.
   */
  function remove(key, attributes) {
    set(key, '', assign({}, attributes, { expires: -1 }));
  }

  /**
   * Create a new instance with additional attributes.
   * @param {Object} attributes - Additional attributes to merge with defaults.
   * @returns {Object} - A new cookie utility instance.
   */
  function withAttributes(attributes) {
    return init(converter, assign({}, defaultAttributes, attributes));
  }

  /**
   * Create a new instance with a custom converter.
   * @param {Object} customConverter - The custom converter to merge with the default.
   * @returns {Object} - A new cookie utility instance.
   */
  function withConverter(customConverter) {
    return init(assign({}, converter, customConverter), defaultAttributes);
  }

  // Return an object with cookie utility methods
  return Object.freeze({
    set,
    get,
    remove,
    withAttributes,
    withConverter,
    attributes: Object.freeze(defaultAttributes),
    converter: Object.freeze(converter),
  });
}

// Export the default instance with the default converter and path attribute
export default init(defaultConverter, { path: '/' });