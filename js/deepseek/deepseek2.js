import Resource from './resource';
import defaultResolver from './default-resolver';

// GraphQL
import shopQuery from './graphql/shopQuery.graphql';
import shopPolicyQuery from './graphql/shopPolicyQuery.graphql';

/**
 * The JS Buy SDK shop resource.
 * Provides methods to fetch shop information and policies.
 * @class
 */
class ShopResource extends Resource {
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
    return this.sendGraphQLQuery(shopQuery, 'shop');
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
    return this.sendGraphQLQuery(shopPolicyQuery, 'shop');
  }

  /**
   * Sends a GraphQL query and resolves the response using the default resolver.
   * @private
   * @param {string} query - The GraphQL query to send.
   * @param {string} resolverKey - The key to use for resolving the response.
   * @return {Promise|GraphModel} A promise resolving with the resolved `GraphModel`.
   */
  sendGraphQLQuery(query, resolverKey) {
    return this.graphQLClient
      .send(query)
      .then(defaultResolver(resolverKey));
  }
}

export default ShopResource;