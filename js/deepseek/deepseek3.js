/**
 * Sorts an array using the QuickSort algorithm.
 * @param {number[]} array - The array to be sorted.
 * @returns {number[]} - The sorted array.
 */
const quickSort = (array = []) => {
    // Base case: if the array is empty or has one element, it's already sorted
    if (array.length <= 1) {
      return array;
    }
  
    // Choose the first element as the pivot
    const pivot = array[0];
    const left = [];
    const right = [];
  
    // Partition the array into elements less than and greater than the pivot
    for (let i = 1; i < array.length; i++) {
      if (array[i] < pivot) {
        left.push(array[i]);
      } else {
        right.push(array[i]);
      }
    }
  
    // Recursively sort the left and right partitions, then combine them with the pivot
    return [...quickSort(left), pivot, ...quickSort(right)];
  };
  
  // Example Usage:
  // const myArray = [2, 4, 1, 6, -7, 8, 5, 9, 3, 4];
  // console.log(quickSort(myArray)); // Output: [-7, 1, 2, 3, 4, 4, 5, 6, 8, 9]