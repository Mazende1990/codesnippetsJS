#!/usr/bin/env python3
from .hash_table import HashTable
from .number_theory.prime_numbers import check_prime, next_prime


class DoubleHash(HashTable):
    """
    Hash Table implementation with open addressing and Double Hashing collision resolution.
    
    Attributes:
        Inherits all attributes from HashTable.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the DoubleHash table with given arguments."""
        super().__init__(*args, **kwargs)

    def __hash_function_2(self, value: int, data: int) -> int:
        """
        Compute the secondary hash value for double hashing.
        
        Args:
            value: The initial hash value.
            data: The data being stored.
            
        Returns:
            The secondary hash value.
        """
        base = value % self.size_table
        next_prime_gt = next_prime(base) if not check_prime(base) else base
        return next_prime_gt - (data % next_prime_gt)

    def __hash_double_function(self, key: int, data: int, increment: int) -> int:
        """
        Compute the double hash function value.
        
        Args:
            key: The original key.
            data: The data being stored.
            increment: The current probe number.
            
        Returns:
            The computed hash index.
        """
        return (increment * self.__hash_function_2(key, data)) % self.size_table

    def _collision_resolution(self, key, data=None) -> int:
        """
        Resolve collisions using double hashing.
        
        Args:
            key: The key being inserted.
            data: The data being stored (optional).
            
        Returns:
            The index where the key should be placed.
        """
        new_key = self.hash_function(data)
        i = 1

        while self.values[new_key] is not None and self.values[new_key] != key:
            if self.balanced_factor() >= self.lim_charge:
                new_key = self.__hash_double_function(key, data, i)
                i += 1
            else:
                new_key = None
                break

        return new_key