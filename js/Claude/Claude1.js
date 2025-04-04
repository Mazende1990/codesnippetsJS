import Queue from '../../../data-structures/queue/Queue';

/**
 * @typedef {Object} TraversalCallbacks
 * @property {function(node: BinaryTreeNode, child: BinaryTreeNode): boolean} allowTraversal - 
 *   Determines whether BFS should traverse from the node to its child.
 * @property {function(node: BinaryTreeNode)} enterNode - Called when BFS enters the node.
 * @property {function(node: BinaryTreeNode)} leaveNode - Called when BFS leaves the node.
 */

/**
 * Initialize traversal callbacks with default implementations if not provided.
 * 
 * @param {TraversalCallbacks} [callbacks={}] - User-provided callbacks
 * @returns {TraversalCallbacks} - Fully initialized callbacks
 */
function initializeCallbacks(callbacks = {}) {
  return {
    allowTraversal: callbacks.allowTraversal || (() => true),
    enterNode: callbacks.enterNode || (() => {}),
    leaveNode: callbacks.leaveNode || (() => {})
  };
}

/**
 * Performs a breadth-first traversal of a binary tree.
 * 
 * @param {BinaryTreeNode} rootNode - The root node to start traversal from
 * @param {TraversalCallbacks} [callbacks={}] - Callbacks for customizing the traversal
 */
export default function breadthFirstSearch(rootNode, callbacks = {}) {
  const normalizedCallbacks = initializeCallbacks(callbacks);
  const nodeQueue = new Queue();
  
  nodeQueue.enqueue(rootNode);
  
  while (!nodeQueue.isEmpty()) {
    const currentNode = nodeQueue.dequeue();
    
    normalizedCallbacks.enterNode(currentNode);
    
    // Enqueue children if traversal is allowed
    enqueueChildrenIfAllowed(currentNode, nodeQueue, normalizedCallbacks);
    
    normalizedCallbacks.leaveNode(currentNode);
  }
}

/**
 * Helper function to enqueue child nodes if traversal is allowed.
 * 
 * @param {BinaryTreeNode} node - Current node being processed
 * @param {Queue} queue - Queue for BFS traversal
 * @param {TraversalCallbacks} callbacks - Traversal callbacks
 */
function enqueueChildrenIfAllowed(node, queue, callbacks) {
  // Try to enqueue left child
  if (node.left && callbacks.allowTraversal(node, node.left)) {
    queue.enqueue(node.left);
  }
  
  // Try to enqueue right child
  if (node.right && callbacks.allowTraversal(node, node.right)) {
    queue.enqueue(node.right);
  }
}