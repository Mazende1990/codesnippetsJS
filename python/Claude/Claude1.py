#!/usr/bin/env python3
from .hash_table import HashTable
from .number_theory.prime_numbers import check_prime, next_prime


class DoubleHash(HashTable):
    """
    Hash Table implementation with open addressing and Double Hash collision resolution.
    
    Double hashing uses a secondary hash function to determine the step size
    when a collision occurs, which helps avoid clustering.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_secondary_prime(self, value):
        """
        Calculate a prime number to use in the secondary hash function.
        
        Args:
            value: The value to derive a prime from
            
        Returns:
            A prime number less than or equal to (value % self.size_table)
        """
        hash_mod = value % self.size_table
        
        if check_prime(hash_mod):
            return hash_mod
        else:
            return next_prime(hash_mod)

    def _calculate_second_hash(self, key, data):
        """
        Secondary hash function for double hashing.
        
        Args:
            key: The original key
            data: The data being stored
            
        Returns:
            An integer to use for probing step size
        """
        prime = self._get_secondary_prime(key)
        return prime - (data % prime)

    def _calculate_probe_position(self, key, data, iteration):
        """
        Calculate the next position to probe based on double hashing.
        
        Args:
            key: The original key
            data: The data being stored
            iteration: Current probe iteration
            
        Returns:
            The next position to check in the hash table
        """
        step = self._calculate_second_hash(key, data)
        return (iteration * step) % self.size_table

    def _collision_resolution(self, key, data=None):
        """
        Resolve collisions using double hashing.
        
        Args:
            key: The key for the hash table
            data: The data to be stored
            
        Returns:
            A new key position or None if the table needs to be resized
        """
        iteration = 1
        position = self.hash_function(data)

        # Check if the current position is available or matches our key
        while self.values[position] is not None and self.values[position] != key:
            # Check if table is getting too full
            if self.balanced_factor() >= self.lim_charge:
                # Table is too full, needs resizing
                return None
            
            # Calculate next position using double hashing
            position = self._calculate_probe_position(key, data, iteration)
            iteration += 1

        return position