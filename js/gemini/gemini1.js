import Queue from '../../../data-structures/queue/Queue';

/**
 * @typedef {Object} Callbacks
 * @property {function(node: BinaryTreeNode, child: BinaryTreeNode): boolean} allowTraversal -
 * Determines whether DFS should traverse from the node to its child.
 * @property {function(node: BinaryTreeNode)} enterNode - Called when DFS enters the node.
 * @property {function(node: BinaryTreeNode)} leaveNode - Called when DFS leaves the node.
 */

/**
 * Initializes callback functions with default values if not provided.
 *
 * @param {Callbacks} [callbacks] - Optional callback object.
 * @returns {Callbacks} - Initialized callback object.
 */
function initializeCallbacks(callbacks = {}) {
  const defaultCallbacks = {
    allowTraversal: () => true,
    enterNode: () => {},
    leaveNode: () => {},
  };

  return {
    allowTraversal: callbacks.allowTraversal || defaultCallbacks.allowTraversal,
    enterNode: callbacks.enterNode || defaultCallbacks.enterNode,
    leaveNode: callbacks.leaveNode || defaultCallbacks.leaveNode,
  };
}

/**
 * Performs breadth-first search on a binary tree.
 *
 * @param {BinaryTreeNode} rootNode - The root node of the binary tree.
 * @param {Callbacks} [originalCallbacks] - Optional callback object.
 */
export default function breadthFirstSearch(rootNode, originalCallbacks) {
  const callbacks = initializeCallbacks(originalCallbacks);
  const nodeQueue = new Queue();

  nodeQueue.enqueue(rootNode);

  while (!nodeQueue.isEmpty()) {
    const currentNode = nodeQueue.dequeue();

    callbacks.enterNode(currentNode);

    const traverseChild = (child) => {
      if (child && callbacks.allowTraversal(currentNode, child)) {
        nodeQueue.enqueue(child);
      }
    };

    traverseChild(currentNode.left);
    traverseChild(currentNode.right);

    callbacks.leaveNode(currentNode);
  }
}