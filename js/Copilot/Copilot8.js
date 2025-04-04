import assign from './assign.mjs';
import defaultConverter from './converter.mjs';

function init(converter, defaultAttributes) {
  function set(key, value, attributes) {
    if (typeof document === 'undefined') {
      return;
    }

    attributes = assign({}, defaultAttributes, attributes);

    if (typeof attributes.expires === 'number') {
      attributes.expires = new Date(Date.now() + attributes.expires * 864e5);
    }
    if (attributes.expires) {
      attributes.expires = attributes.expires.toUTCString();
    }

    key = encodeURIComponent(key)
      .replace(/%(2[346B]|5E|60|7C)/g, decodeURIComponent)
      .replace(/[()]/g, escape);

    value = converter.write(value, key);

    let stringifiedAttributes = '';
    for (const attributeName in attributes) {
      if (!attributes[attributeName]) {
        continue;
      }

      stringifiedAttributes += `; ${attributeName}`;

      if (attributes[attributeName] === true) {
        continue;
      }

      // Considers RFC 6265 section 5.2:
      // ...
      // 3.  If the remaining unparsed-attributes contains a %x3B (";")
      //     character:
      // Consume the characters of the unparsed-attributes up to,
      // not including, the first %x3B (";") character.
      // ...
      stringifiedAttributes += `=${attributes[attributeName].split(';')[0]}`;
    }

    document.cookie = `${key}=${value}${stringifiedAttributes}`;
  }

  function get(key) {
    if (typeof document === 'undefined' || (arguments.length && !key)) {
      return;
    }

    // To prevent the for loop in the first place assign an empty array
    // in case there are no cookies at all.
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    const jar = {};
    for (const cookie of cookies) {
      const parts = cookie.split('=');
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
      } catch (e) {}
    }

    return key ? jar[key] : jar;
  }

  return Object.create(
    {
      set,
      get,
      remove(key, attributes) {
        set(key, '', assign({}, attributes, { expires: -1 }));
      },
      withAttributes(attributes) {
        return init(this.converter, assign({}, this.attributes, attributes));
      },
      withConverter(converter) {
        return init(assign({}, this.converter, converter), this.attributes);
      }
    },
    {
      attributes: { value: Object.freeze(defaultAttributes) },
      converter: { value: Object.freeze(converter) }
    }
  );
}

export default init(defaultConverter, { path: '/' });