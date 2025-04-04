const quickSort = (array = []) => {
    if (array.length === 0) return [];
  
    const [pivot, ...rest] = array;
    const left = rest.filter(item => item < pivot);
    const right = rest.filter(item => item >= pivot);
  
    return [...quickSort(left), pivot, ...quickSort(right)];
  };
  
  // Example Usage:
  const myArray = [2, 4, 1, 6, -7, 8, 5, 9, 3, 4];
  console.log(quickSort(myArray));