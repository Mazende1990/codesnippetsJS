import Resource from './resource';
import defaultResolver from './default-resolver';

// GraphQL Queries
import shopQuery from './graphql/shopQuery.graphql';
import shopPolicyQuery from './graphql/shopPolicyQuery.graphql';

/**
 * The JS Buy SDK shop resource
 * @class
 */
class ShopResource extends Resource {
  
  /**
   * Generic method to fetch shop data.
   *
   * @param {string} query - The GraphQL query to execute.
   * @return {Promise|GraphModel} A promise resolving with a `GraphModel` of the shop.
   * @private
   */
  fetchShopData(query) {
    return this.graphQLClient.send(query).then(defaultResolver('shop'));
  }

  /**
   * Fetches shop information (`currencyCode`, `description`, `moneyFormat`, `name`, and `primaryDomain`).
   * See the {@link https://help.shopify.com/api/storefront-api/reference/object/shop|Storefront API reference} for more information.
   *
   * @example
   * client.shop.fetchInfo().then((shop) => {
   *   // Do something with the shop
   * });
   *
   * @return {Promise|GraphModel} A promise resolving with a `GraphModel` of the shop.
   */
  fetchInfo() {
    return this.fetchShopData(shopQuery);
  }

  /**
   * Fetches shop policies (privacy policy, terms of service, and refund policy).
   *
   * @example
   * client.shop.fetchPolicies().then((shop) => {
   *   // Do something with the shop
   * });
   *
   * @return {Promise|GraphModel} A promise resolving with a `GraphModel` of the shop.
   */
  fetchPolicies() {
    return this.fetchShopData(shopPolicyQuery);
  }
}

export default ShopResource;
