# Copyright (C) 2019 Databricks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Additional Spark functions used in Koalas (now pandas API on Spark).

This module provides extended Spark SQL functions that are compatible with pandas API on Spark.
"""

from pyspark import SparkContext
from pyspark.sql.column import Column, _to_java_column, _to_seq, _create_column_from_literal

__all__ = ["percentile_approx", "array_repeat", "repeat"]

def _call_udf(sc, name, *cols):
    """Internal function to call a UDF with the given arguments."""
    return Column(sc._jvm.functions.callUDF(name, _make_arguments(sc, *cols)))

def _make_arguments(sc, *cols):
    """Convert Python columns to Java array of Columns."""
    java_arr = sc._gateway.new_array(sc._jvm.Column, len(cols))
    for i, col in enumerate(cols):
        java_arr[i] = col
    return java_arr

def percentile_approx(col, percentage, accuracy=10000):
    """
    Returns the approximate percentile value of numeric column at given percentage(s).
    
    Args:
        col: The numeric column to compute percentiles on
        percentage: Single value or list of values between 0.0 and 1.0
        accuracy: Controls approximation accuracy (default: 10000)
    
    Returns:
        Column: Approximate percentile value(s) as a Spark Column
    
    Examples:
        >>> df.select(percentile_approx(df.value, 0.5)).show()
        >>> df.select(percentile_approx(df.value, [0.25, 0.5, 0.75])).show()
    
    Notes:
        Higher accuracy values yield better precision but use more memory.
        1.0/accuracy is the relative error of the approximation.
        Ported from Spark 3.1.
    """
    sc = SparkContext._active_spark_context
    
    # Convert percentage to appropriate Java Column type
    if isinstance(percentage, (list, tuple)):
        percentage = sc._jvm.functions.array(
            _to_seq(sc, [_create_column_from_literal(x) for x in percentage])
        )
    elif isinstance(percentage, Column):
        percentage = _to_java_column(percentage)
    else:
        percentage = _create_column_from_literal(percentage)
    
    # Convert accuracy to appropriate Java Column type
    accuracy = (
        _to_java_column(accuracy)
        if isinstance(accuracy, Column)
        else _create_column_from_literal(accuracy)
    )
    
    return _call_udf(sc, "percentile_approx", _to_java_column(col), percentage, accuracy)

def array_repeat(col, count):
    """
    Creates an array containing a column repeated count times.
    
    Args:
        col: The column to repeat
        count: Number of repetitions (integer or Column)
    
    Returns:
        Column: Array column with repeated values
    
    Examples:
        >>> df.select(array_repeat(df.value, 3)).show()
    
    Notes:
        Ported from Spark 3.0.
    """
    sc = SparkContext._active_spark_context
    count_col = _to_java_column(count) if isinstance(count, Column) else count
    return Column(sc._jvm.functions.array_repeat(_to_java_column(col), count_col))

def repeat(col, n):
    """
    Repeats a string column n times, returning a new string column.
    
    Args:
        col: The string column to repeat
        n: Number of repetitions (integer or Column)
    
    Returns:
        Column: Repeated string column
    
    Examples:
        >>> df.select(repeat(df.name, 2)).show()
    """
    sc = SparkContext._active_spark_context
    n_col = _to_java_column(n) if isinstance(n, Column) else _create_column_from_literal(n)
    return _call_udf(sc, "repeat", _to_java_column(col), n_col)