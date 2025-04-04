import Queue from '../../../data-structures/queue/Queue';

/**
 * @typedef {Object} Callbacks
 * @property {function(node: BinaryTreeNode, child: BinaryTreeNode): boolean} allowTraversal -
 *   Determines whether DFS should traverse from the node to its child.
 * @property {function(node: BinaryTreeNode)} enterNode - Called when DFS enters the node.
 * @property {function(node: BinaryTreeNode)} leaveNode - Called when DFS leaves the node.
 */

/**
 * @param {Callbacks} [callbacks={}]
 * @returns {Callbacks}
 */
function initCallbacks(callbacks = {}) {
  return {
    allowTraversal: callbacks.allowTraversal || (() => true),
    enterNode: callbacks.enterNode || (() => {}),
    leaveNode: callbacks.leaveNode || (() => {}),
  };
}

/**
 * @param {BinaryTreeNode} rootNode
 * @param {Callbacks} [originalCallbacks]
 */
export default function breadthFirstSearch(rootNode, originalCallbacks) {
  callbacks = initCallbacks(originalCallbacks);
  const nodeQueue = new Queue();

  // Initialize the queue with the root node.
  nodeQueue.enqueue(rootNode);

  while (!nodeQueue.isEmpty()) {
    const currentNode = nodeQueue.dequeue();

    callbacks.enterNode(currentNode);

    // Traverse left child if allowed.
    if (currentNode.left && callbacks.allowTraversal(currentNode, currentNode.left)) {
      nodeQueue.enqueue(currentNode.left);
    }

    // Traverse right child if allowed.
    if (currentNode.right && callbacks.allowTraversal(currentNode, currentNode.right)) {
      nodeQueue.enqueue(currentNode.right);
    }

    callbacks.leaveNode(currentNode);
  }
}