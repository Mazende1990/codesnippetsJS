/**
 * Sorts an array using the quicksort algorithm.
 *
 * @param {Array} array - The array to be sorted
 * @returns {Array} A new sorted array
 */
const quickSort = (array = []) => {
    // Base case: empty or single-element arrays are already sorted
    if (array.length <= 1) {
      return array;
    }
    
    // Choose the first element as pivot
    const pivot = array[0];
    
    // Partition the array into elements less than and greater than the pivot
    const lessThanPivot = [];
    const greaterThanPivot = [];
    
    // Start from index 1 since index 0 is the pivot
    for (let i = 1; i < array.length; i++) {
      const currentElement = array[i];
      
      if (currentElement < pivot) {
        lessThanPivot.push(currentElement);
      } else {
        greaterThanPivot.push(currentElement);
      }
    }
    
    // Recursively sort both partitions and combine with the pivot
    return [
      ...quickSort(lessThanPivot),
      pivot,
      ...quickSort(greaterThanPivot)
    ];
  };
  
  // Example Usage:
  // const unsortedArray = [2, 4, 1, 6, -7, 8, 5, 9, 3, 4];
  // console.log(quickSort(unsortedArray));
  // Output: [-7, 1, 2, 3, 4, 4, 5, 6, 8, 9]