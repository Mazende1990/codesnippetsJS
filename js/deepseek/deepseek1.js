import Queue from '../../../data-structures/queue/Queue';

/**
 * @typedef {Object} Callbacks
 * @property {function(node: BinaryTreeNode, child: BinaryTreeNode): boolean} allowTraversal -
 *   Determines whether BFS should traverse from the node to its child.
 * @property {function(node: BinaryTreeNode)} enterNode - Called when BFS enters the node.
 * @property {function(node: BinaryTreeNode)} leaveNode - Called when BFS leaves the node.
 */

/**
 * Initializes the callbacks for BFS traversal.
 * @param {Callbacks} [callbacks={}] - The callbacks to initialize.
 * @returns {Callbacks} - The initialized callbacks.
 */
function initCallbacks(callbacks = {}) {
  const {
    allowTraversal = () => true,
    enterNode = () => {},
    leaveNode = () => {},
  } = callbacks;

  return { allowTraversal, enterNode, leaveNode };
}

/**
 * Enqueues the child node if traversal is allowed.
 * @param {Queue} queue - The queue to enqueue the child node.
 * @param {BinaryTreeNode} parentNode - The parent node.
 * @param {BinaryTreeNode} childNode - The child node.
 * @param {function} allowTraversal - The callback to determine if traversal is allowed.
 */
function enqueueChildIfAllowed(queue, parentNode, childNode, allowTraversal) {
  if (childNode && allowTraversal(parentNode, childNode)) {
    queue.enqueue(childNode);
  }
}

/**
 * Performs Breadth-First Search (BFS) on a binary tree.
 * @param {BinaryTreeNode} rootNode - The root node of the tree.
 * @param {Callbacks} [originalCallbacks={}] - The callbacks for BFS traversal.
 */
export default function breadthFirstSearch(rootNode, originalCallbacks = {}) {
  const callbacks = initCallbacks(originalCallbacks);
  const nodeQueue = new Queue();

  nodeQueue.enqueue(rootNode);

  while (!nodeQueue.isEmpty()) {
    const currentNode = nodeQueue.dequeue();

    callbacks.enterNode(currentNode);

    // Enqueue left and right children if traversal is allowed
    enqueueChildIfAllowed(nodeQueue, currentNode, currentNode.left, callbacks.allowTraversal);
    enqueueChildIfAllowed(nodeQueue, currentNode, currentNode.right, callbacks.allowTraversal);

    callbacks.leaveNode(currentNode);
  }
}