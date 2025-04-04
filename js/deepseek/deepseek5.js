/*
 * @lc app=leetcode id=215 lang=javascript
 *
 * [215] Kth Largest Element in an Array
 */

/**
 * Max-heapifies the array by ensuring the parent nodes are greater than their children.
 * @param {number[]} nums - The array to heapify.
 * @returns {number} - The maximum element (root of the heap).
 */
function maxHeapify(nums) {
    // Add a dummy element at the beginning to simplify parent-child index calculations
    nums.unshift(null);
  
    // Heapify from the last element to the root
    for (let i = nums.length - 1; i >> 1 > 0; i--) {
      // If the current node is greater than its parent, swap them
      if (nums[i] > nums[i >> 1]) {
        [nums[i], nums[i >> 1]] = [nums[i >> 1], nums[i]];
      }
    }
  
    // Remove the dummy element and return the root (max element)
    nums.shift();
    return nums[0];
  }
  
  /**
   * Finds the kth largest element in an array using a max-heap approach.
   * @param {number[]} nums - The input array.
   * @param {number} k - The kth largest element to find.
   * @returns {number} - The kth largest element.
   */
  const findKthLargest = function (nums, k) {
    let result = null;
  
    // Perform heapify k times to extract the kth largest element
    for (let i = 0; i < k; i++) {
      result = maxHeapify(nums); // Heapify and get the max element
      nums.shift(); // Remove the max element from the array
    }
  
    return result;
  };
  
  // Example usage:
  console.log(findKthLargest([1, 2, 3, 4, 5], 2)); // Output: 4