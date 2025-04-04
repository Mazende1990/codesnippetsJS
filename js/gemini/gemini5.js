/**
 * @lc app=leetcode id=215 lang=javascript
 *
 * [215] Kth Largest Element in an Array
 */

/**
 * Converts an array into a max heap and returns the maximum element.
 *
 * @param {number[]} nums - The array to be converted into a max heap.
 * @returns {number} - The maximum element in the heap.
 */
function maxHeapify(nums) {
    nums.unshift(null); // Add a placeholder at the beginning for 1-based indexing.
  
    for (let i = Math.floor(nums.length / 2); i > 0; i--) {
      // Heapify from the bottom up.
      if (nums[i * 2] !== undefined && nums[i * 2] > nums[i]) {
        // If the left child is larger, swap.
        let temp = nums[i];
        nums[i] = nums[i * 2];
        nums[i * 2] = temp;
      }
      if (nums[i * 2 + 1] !== undefined && nums[i * 2 + 1] > nums[i]) {
        // If the right child is larger, swap.
        let temp = nums[i];
        nums[i] = nums[i * 2 + 1];
        nums[i * 2 + 1] = temp;
      }
    }
  
    nums.shift(); // Remove the placeholder.
    return nums[0]; // Return the maximum element (root of the heap).
  }
  
  /**
   * Finds the kth largest element in an array.
   *
   * @param {number[]} nums - The input array.
   * @param {number} k - The kth largest element to find.
   * @returns {number} - The kth largest element.
   */
  const findKthLargest = (nums, k) => {
    // Heap based solution, O(k log n) time complexity.
    let heap = [...nums]; // Create a copy of the array to avoid modifying the original.
    let result = null;
  
    for (let i = 0; i < k; i++) {
      result = maxHeapify(heap);
      heap.shift(); // Remove the maximum element after each heapify.
    }
  
    return result;
  };
  
  // Example Usage:
  // console.log(findKthLargest([1, 2, 3, 4, 5], 2)); // Output: 4