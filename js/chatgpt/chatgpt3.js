const quickSort = (array = []) => {
    if (array.length <= 1) return array; // Base case: Return if 0 or 1 element

    const [pivot, ...rest] = array; // Destructure first element as pivot
    const left = rest.filter(num => num < pivot); // Elements less than pivot
    const right = rest.filter(num => num >= pivot); // Elements greater or equal

    return [...quickSort(left), pivot, ...quickSort(right)];
};

// Example Usage:
const myArray = [2, 4, 1, 6, -7, 8, 5, 9, 3, 4];
console.log(quickSort(myArray));
