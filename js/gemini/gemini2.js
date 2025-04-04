import Resource from './resource';
import defaultResolver from './default-resolver';

// GraphQL
import shopQuery from './graphql/shopQuery.graphql';
import shopPolicyQuery from './graphql/shopPolicyQuery.graphql';

/**
 * The JS Buy SDK shop resource.
 */
class ShopResource extends Resource {
  /**
   * Fetches core shop information.
   *
   * Retrieves details such as `currencyCode`, `description`, `moneyFormat`, `name`, and `primaryDomain`.
   * Refer to the {@link https://help.shopify.com/api/storefront-api/reference/object/shop|Storefront API reference} for comprehensive information.
   *
   * @async
   * @returns {Promise<GraphModel>} A promise resolving with a `GraphModel` of the shop.
   *
   * @example
   * client.shop.fetchInfo().then((shop) => {
   * // Process the shop data
   * console.log(shop);
   * });
   */
  async fetchInfo() {
    const response = await this.graphQLClient.send(shopQuery);
    return defaultResolver('shop')(response);
  }

  /**
   * Fetches shop policies.
   *
   * Retrieves the shop's privacy policy, terms of service, and refund policy.
   *
   * @async
   * @returns {Promise<GraphModel>} A promise resolving with a `GraphModel` containing shop policies.
   *
   * @example
   * client.shop.fetchPolicies().then((policies) => {
   * // Process the shop policies
   * console.log(policies);
   * });
   */
  async fetchPolicies() {
    const response = await this.graphQLClient.send(shopPolicyQuery);
    return defaultResolver('shop')(response);
  }
}

export default ShopResource;