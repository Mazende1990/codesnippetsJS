import assign from './assign.mjs';
import defaultConverter from './converter.mjs';

/**
 * Create a cookie handler with the specified converter and default attributes
 * @param {Object} converter - Converter with read/write methods for cookie values
 * @param {Object} defaultAttributes - Default cookie attributes
 * @returns {Object} Cookie handler with get, set, remove methods
 */
function init(converter, defaultAttributes) {
  /**
   * Sets a cookie with the given key, value, and attributes
   * @param {string} key - Cookie name
   * @param {string} value - Cookie value
   * @param {Object} attributes - Cookie attributes (path, domain, expires, etc.)
   * @returns {string|undefined} The cookie string or undefined if document is not available
   */
  function set(key, value, attributes) {
    if (typeof document === 'undefined') {
      return;
    }

    // Merge attributes with defaults
    attributes = assign({}, defaultAttributes, attributes);

    // Handle expires attribute
    if (typeof attributes.expires === 'number') {
      attributes.expires = new Date(Date.now() + attributes.expires * 864e5); // 864e5 = 24 * 60 * 60 * 1000 (days to ms)
    }
    if (attributes.expires) {
      attributes.expires = attributes.expires.toUTCString();
    }

    // Encode key properly
    key = encodeURIComponent(key)
      .replace(/%(2[346B]|5E|60|7C)/g, decodeURIComponent)
      .replace(/[()]/g, escape);

    // Convert value
    value = converter.write(value, key);

    // Build attribute string
    const stringifiedAttributes = buildAttributeString(attributes);

    // Set the cookie
    return (document.cookie = key + '=' + value + stringifiedAttributes);
  }

  /**
   * Builds the attribute string portion of the cookie
   * @private
   * @param {Object} attributes - Cookie attributes
   * @returns {string} Formatted attribute string
   */
  function buildAttributeString(attributes) {
    let result = '';
    
    for (const attributeName in attributes) {
      if (!attributes[attributeName]) {
        continue;
      }

      result += '; ' + attributeName;

      if (attributes[attributeName] === true) {
        continue;
      }

      // Considers RFC 6265 section 5.2:
      // Only use the part before the first semicolon if present
      result += '=' + attributes[attributeName].split(';')[0];
    }
    
    return result;
  }

  /**
   * Gets a cookie value by key, or all cookies if no key is provided
   * @param {string} [key] - Cookie name to retrieve
   * @returns {Object|string|undefined} Cookie value, object of all cookies, or undefined
   */
  function get(key) {
    if (typeof document === 'undefined' || (arguments.length && !key)) {
      return;
    }

    // Parse all cookies
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    const jar = parseCookiesToJar(cookies, key);
    
    return key ? jar[key] : jar;
  }

  /**
   * Parses cookies into a jar object
   * @private
   * @param {Array} cookies - Array of cookie strings
   * @param {string} [targetKey] - Optional key to stop parsing once found
   * @returns {Object} Object with cookie key-value pairs
   */
  function parseCookiesToJar(cookies, targetKey) {
    const jar = {};
    
    for (let i = 0; i < cookies.length; i++) {
      const parts = cookies[i].split('=');
      const value = parts.slice(1).join('=');
      
      // Remove quotes if present
      const unquotedValue = value[0] === '"' ? value.slice(1, -1) : value;
      
      try {
        const foundKey = defaultConverter.read(parts[0]);
        jar[foundKey] = converter.read(unquotedValue, foundKey);
        
        // Early exit if we found the target key
        if (targetKey === foundKey) {
          break;
        }
      } catch (e) {
        // Silently ignore parsing errors
      }
    }
    
    return jar;
  }

  /**
   * Removes a cookie by setting its expiration in the past
   * @param {string} key - Cookie name to remove
   * @param {Object} attributes - Cookie attributes
   */
  function remove(key, attributes) {
    set(
      key,
      '',
      assign({}, attributes, {
        expires: -1
      })
    );
  }

  /**
   * Creates a new cookie handler with merged attributes
   * @param {Object} attributes - Attributes to merge with existing ones
   * @returns {Object} New cookie handler
   */
  function withAttributes(attributes) {
    return init(this.converter, assign({}, this.attributes, attributes));
  }

  /**
   * Creates a new cookie handler with merged converter
   * @param {Object} converter - Converter to merge with existing one
   * @returns {Object} New cookie handler
   */
  function withConverter(converter) {
    return init(assign({}, this.converter, converter), this.attributes);
  }

  // Create and return the cookie handler object
  return Object.create(
    {
      set,
      get,
      remove,
      withAttributes,
      withConverter
    },
    {
      attributes: { value: Object.freeze(defaultAttributes) },
      converter: { value: Object.freeze(converter) }
    }
  );
}

// Export the default cookie handler with path='/'
export default init(defaultConverter, { path: '/' });