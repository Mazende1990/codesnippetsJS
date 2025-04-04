import Queue from '../../../data-structures/queue/Queue';

/**
 * @typedef {Object} Callbacks
 * @property {(node: BinaryTreeNode, child: BinaryTreeNode) => boolean} allowTraversal
 *   Determines whether DFS should traverse from the node to its child.
 * @property {(node: BinaryTreeNode) => void} enterNode
 *   Called when DFS enters the node.
 * @property {(node: BinaryTreeNode) => void} leaveNode
 *   Called when DFS leaves the node.
 */

/**
 * Initializes callbacks with defaults if not provided.
 *
 * @param {Callbacks} [callbacks={}]
 * @returns {Callbacks}
 */
function initCallbacks({
  allowTraversal = () => true,
  enterNode = () => {},
  leaveNode = () => {},
} = {}) {
  return { allowTraversal, enterNode, leaveNode };
}

/**
 * Performs a breadth-first search (BFS) on a binary tree.
 *
 * @param {BinaryTreeNode} rootNode
 * @param {Callbacks} [originalCallbacks]
 */
export default function breadthFirstSearch(rootNode, originalCallbacks) {
  if (!rootNode) return;

  const callbacks = initCallbacks(originalCallbacks);
  const nodeQueue = new Queue();

  nodeQueue.enqueue(rootNode);

  while (!nodeQueue.isEmpty()) {
    const currentNode = nodeQueue.dequeue();

    callbacks.enterNode(currentNode);

    // Enqueue children if traversal is allowed.
    for (const child of [currentNode.left, currentNode.right]) {
      if (child && callbacks.allowTraversal(currentNode, child)) {
        nodeQueue.enqueue(child);
      }
    }

    callbacks.leaveNode(currentNode);
  }
}
