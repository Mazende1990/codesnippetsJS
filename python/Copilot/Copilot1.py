#!/usr/bin/env python3
from .hash_table import HashTable
from .number_theory.prime_numbers import check_prime, next_prime


class DoubleHash(HashTable):
    """
    Hash Table example with open addressing and Double Hash
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __hash_function_2(self, value, data):
        """
        Secondary hash function for double hashing.
        """
        remainder = value % self.size_table
        next_prime_gt = next_prime(remainder) if not check_prime(remainder) else remainder
        return next_prime_gt - (data % next_prime_gt)

    def __hash_double_function(self, key, data, increment):
        """
        Double hash function combining primary and secondary hash functions.
        """
        return (increment * self.__hash_function_2(key, data)) % self.size_table

    def _collision_resolution(self, key, data=None):
        """
        Resolve collisions using double hashing.
        """
        i = 1
        new_key = self.hash_function(data)

        while self.values[new_key] is not None and self.values[new_key] != key:
            if self.balanced_factor() >= self.lim_charge:
                new_key = self.__hash_double_function(key, data, i)
                i += 1
            else:
                new_key = None
                break

        return new_key