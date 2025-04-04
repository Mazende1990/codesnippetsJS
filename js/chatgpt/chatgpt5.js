/**
 * @lc app=leetcode id=215 lang=javascript
 *
 * [215] Kth Largest Element in an Array
 */

/**
 * Helper function to maintain a max heap property.
 * Swaps down elements in a heap to maintain order.
 *
 * @param {number[]} heap
 * @param {number} index
 * @param {number} heapSize
 */
const heapify = (heap, index, heapSize) => {
    let largest = index;
    const left = 2 * index + 1;
    const right = 2 * index + 2;
  
    if (left < heapSize && heap[left] > heap[largest]) {
      largest = left;
    }
  
    if (right < heapSize && heap[right] > heap[largest]) {
      largest = right;
    }
  
    if (largest !== index) {
      [heap[index], heap[largest]] = [heap[largest], heap[index]];
      heapify(heap, largest, heapSize);
    }
  };
  
  /**
   * Builds a max heap from an array.
   *
   * @param {number[]} nums
   */
  const buildMaxHeap = (nums) => {
    const n = nums.length;
    for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
      heapify(nums, i, n);
    }
  };
  
  /**
   * Finds the k-th largest element in an array using a heap.
   *
   * @param {number[]} nums
   * @param {number} k
   * @return {number}
   */
  const findKthLargest = (nums, k) => {
    buildMaxHeap(nums);
    
    for (let i = nums.length - 1; i > nums.length - k - 1; i--) {
      [nums[0], nums[i]] = [nums[i], nums[0]]; // Swap max element to the end
      heapify(nums, 0, i); // Restore heap property
    }
    
    return nums[nums.length - k];
  };
  
  // Example Usage
  console.log(findKthLargest([3, 2, 1, 5, 6, 4], 2)); // Output: 5
  console.log(findKthLargest([1, 2, 3, 4, 5], 2)); // Output: 4
  