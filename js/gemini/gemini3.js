/**
 * Sorts an array using the quicksort algorithm.
 *
 * @param {number[]} arry - The array to be sorted. Defaults to an empty array.
 * @returns {number[]} - A new sorted array.
 *
 * @example
 * const myArray = [2, 4, 1, 6, -7, 8, 5, 9, 3, 4];
 * console.log(quickSort(myArray)); // Output: [-7, 1, 2, 3, 4, 4, 5, 6, 8, 9]
 */
const quickSort = (arry = []) => {
    if (arry.length <= 1) {
      return arry; // Base case: an empty or single-element array is already sorted.
    }
  
    const pivot = arry[0];
    const left = [];
    const right = [];
  
    for (let i = 1; i < arry.length; i++) {
      if (arry[i] < pivot) {
        left.push(arry[i]);
      } else {
        right.push(arry[i]);
      }
    }
  
    return [...quickSort(left), pivot, ...quickSort(right)];
  };
  
  // Example Usage:
  // const myArray = [2, 4, 1, 6, -7, 8, 5, 9, 3, 4];
  // console.log(quickSort(myArray));