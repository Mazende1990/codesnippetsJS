/*
 * @lc app=leetcode id=215 lang=javascript
 *
 * [215] Kth Largest Element in an Array
 */

/**
 * Finds the kth largest element in an unsorted array using a max-heap approach.
 * 
 * @param {number[]} nums - Array of numbers
 * @param {number} k - Position of the largest element to find (1-based)
 * @return {number} - The kth largest element
 */
var findKthLargest = function(nums, k) {
    let result = null;
    
    for (let i = 0; i < k; i++) {
      // Build max heap and extract the maximum element k times
      result = extractMaximum(nums);
      nums.shift(); // Remove the maximum element
    }
    
    return result;
  };
  
  /**
   * Builds a max heap from the given array and returns the maximum element.
   * A max heap is a binary tree where the parent node is greater than its children.
   * 
   * @param {number[]} nums - Array to heapify
   * @return {number} - The maximum element (root of the heap)
   */
  function extractMaximum(nums) {
    // Add a null element at index 0 to make the heap math easier
    // (allows using bit shift for parent/child calculations)
    nums.unshift(null);
    
    // Heapify from bottom to top
    for (let i = nums.length - 1; i > 0; i--) {
      const parentIndex = i >> 1; // Same as Math.floor(i/2)
      
      // If parent exists and child is greater than parent
      if (parentIndex > 0 && nums[i] > nums[parentIndex]) {
        // Swap parent and child
        swap(nums, i, parentIndex);
      }
    }
    
    // Remove the null element we added
    nums.shift();
    
    // Return the maximum element (now at index 0)
    return nums[0];
  }
  
  /**
   * Swaps two elements in an array.
   * 
   * @param {Array} array - The array containing elements to swap
   * @param {number} i - Index of first element
   * @param {number} j - Index of second element
   */
  function swap(array, i, j) {
    const temp = array[i];
    array[i] = array[j];
    array[j] = temp;
  }
  
  // Example usage
  // findKthLargest([1, 2, 3, 4, 5], 2); // Returns 4