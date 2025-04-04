/*
 * @lc app=leetcode id=215 lang=javascript
 *
 * [215] Kth Largest Element in an Array
 */

/**
 * @param {number[]} nums
 * @param {number} k
 * @return {number}
 */
function maxHeapify(nums) {
    nums.unshift(null);
  
    for (let i = nums.length - 1; i >> 1 > 0; i--) {
      // Heapify from bottom to top
      if (nums[i] > nums[i >> 1]) {
        // Swap if child is greater than parent
        [nums[i], nums[i >> 1]] = [nums[i >> 1], nums[i]];
      }
    }
    nums.shift();
    return nums[0];
  }
  
  const findKthLargest = (nums, k) => {
    let result = null;
    for (let i = 0; i < k; i++) {
      result = maxHeapify(nums);
      nums.shift();
    }
    return result;
  };
  
  // Example Usage:
  console.log(findKthLargest([1, 2, 3, 4, 5], 2));