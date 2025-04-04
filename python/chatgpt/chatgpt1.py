#!/usr/bin/env python3
from .hash_table import HashTable
from .number_theory.prime_numbers import check_prime, next_prime


class DoubleHash(HashTable):
    """
    Hash Table implementation with open addressing and double hashing for collision resolution.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __calculate_secondary_hash(self, value, data):
        """
        Calculates the secondary hash based on the value and data.
        Uses the next prime number greater than value % table size if it's not prime.
        """
        modulo_value = value % self.size_table
        next_prime_value = next_prime(modulo_value) if not check_prime(modulo_value) else modulo_value
        return next_prime_value - (data % next_prime_value)

    def __calculate_double_hash(self, key, data, increment):
        """
        Combines the primary hash with a secondary hash to resolve collisions.
        The increment is used to find the next available slot.
        """
        secondary_hash = self.__calculate_secondary_hash(key, data)
        return (increment * secondary_hash) % self.size_table

    def _resolve_collision(self, key, data=None):
        """
        Resolves collisions by probing using double hashing.
        Stops if a slot is found or if no further slots are available.
        """
        increment = 1
        current_key = self.hash_function(data)

        while self.values[current_key] is not None and self.values[current_key] != key:
            if self.balanced_factor() >= self.lim_charge:
                current_key = self.__calculate_double_hash(key, data, increment)
                increment += 1
            else:
                return None  # No more slots available

        return current_key
