import Resource from './resource';
import defaultResolver from './default-resolver';

// GraphQL queries
import shopQuery from './graphql/shopQuery.graphql';
import shopPolicyQuery from './graphql/shopPolicyQuery.graphql';

/**
 * The JS Buy SDK shop resource for fetching shop information and policies
 * @class
 */
class ShopResource extends Resource {
  /**
   * Fetches basic shop information including:
   * - currencyCode
   * - description
   * - moneyFormat
   * - name
   * - primaryDomain
   * 
   * @see {@link https://help.shopify.com/api/storefront-api/reference/object/shop|Storefront API reference}
   *
   * @example
   * client.shop.fetchInfo().then((shop) => {
   *   console.log(shop.name);
   *   console.log(shop.currencyCode);
   * });
   *
   * @return {Promise<GraphModel>} A promise resolving with a GraphModel of the shop
   */
  fetchInfo() {
    return this.executeQuery(shopQuery);
  }

  /**
   * Fetches shop policies including:
   * - Privacy policy
   * - Terms of service
   * - Refund policy
   *
   * @example
   * client.shop.fetchPolicies().then((shop) => {
   *   console.log(shop.privacyPolicy);
   *   console.log(shop.termsOfService);
   *   console.log(shop.refundPolicy);
   * });
   *
   * @return {Promise<GraphModel>} A promise resolving with a GraphModel of the shop
   */
  fetchPolicies() {
    return this.executeQuery(shopPolicyQuery);
  }

  /**
   * Helper method to execute GraphQL queries and resolve with shop data
   * 
   * @private
   * @param {Object} query - GraphQL query document
   * @return {Promise<GraphModel>} A promise resolving with shop data
   */
  executeQuery(query) {
    return this.graphQLClient
      .send(query)
      .then(defaultResolver('shop'));
  }
}

export default ShopResource;