import assign from './assign.mjs';
import defaultConverter from './converter.mjs';

/**
 * Initializes a cookie handling object.
 *
 * @param {object} converter - The converter object for reading and writing cookie values.
 * @param {object} defaultAttributes - Default attributes for cookies.
 * @returns {object} - An object with cookie handling methods.
 */
function init(converter, defaultAttributes) {
  /**
   * Sets a cookie.
   *
   * @param {string} key - The cookie key.
   * @param {*} value - The cookie value.
   * @param {object} attributes - Cookie attributes.
   * @returns {string|undefined} - The cookie string, or undefined if not in a browser environment.
   */
  function set(key, value, attributes) {
    if (typeof document === 'undefined') {
      return;
    }

    const mergedAttributes = assign({}, defaultAttributes, attributes);

    if (typeof mergedAttributes.expires === 'number') {
      mergedAttributes.expires = new Date(Date.now() + mergedAttributes.expires * 864e5);
    }
    if (mergedAttributes.expires) {
      mergedAttributes.expires = mergedAttributes.expires.toUTCString();
    }

    const encodedKey = encodeURIComponent(key)
      .replace(/%(2[346B]|5E|60|7C)/g, decodeURIComponent)
      .replace(/[()]/g, escape);

    const convertedValue = converter.write(value, key);

    let stringifiedAttributes = '';
    for (const attributeName in mergedAttributes) {
      if (Object.prototype.hasOwnProperty.call(mergedAttributes, attributeName)) {
        const attributeValue = mergedAttributes[attributeName];
        if (!attributeValue) {
          continue;
        }

        stringifiedAttributes += '; ' + attributeName;

        if (attributeValue === true) {
          continue;
        }

        stringifiedAttributes += '=' + attributeValue.split(';')[0];
      }
    }

    return (document.cookie = encodedKey + '=' + convertedValue + stringifiedAttributes);
  }

  /**
   * Gets a cookie value.
   *
   * @param {string} key - The cookie key.
   * @returns {*} - The cookie value, or an object containing all cookies.
   */
  function get(key) {
    if (typeof document === 'undefined' || (arguments.length && !key)) {
      return;
    }

    const cookies = document.cookie ? document.cookie.split('; ') : [];
    const jar = {};

    for (let i = 0; i < cookies.length; i++) {
      const parts = cookies[i].split('=');
      let value = parts.slice(1).join('=');

      if (value[0] === '"') {
        value = value.slice(1, -1);
      }

      try {
        const foundKey = defaultConverter.read(parts[0]);
        jar[foundKey] = converter.read(value, foundKey);

        if (key === foundKey) {
          break;
        }
      } catch (e) {
        // Ignore parsing errors.
      }
    }

    return key ? jar[key] : jar;
  }

  return Object.create(
    {
      set: set,
      get: get,
      remove: function (key, attributes) {
        set(
          key,
          '',
          assign({}, attributes, {
            expires: -1,
          })
        );
      },
      withAttributes: function (attributes) {
        return init(this.converter, assign({}, this.attributes, attributes));
      },
      withConverter: function (converter) {
        return init(assign({}, this.converter, converter), this.attributes);
      },
    },
    {
      attributes: { value: Object.freeze(defaultAttributes) },
      converter: { value: Object.freeze(converter) },
    }
  );
}

export default init(defaultConverter, { path: '/' });