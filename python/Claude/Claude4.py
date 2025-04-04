#
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
#
"""
Additional Spark functions used in Koalas that may not be available in the current PySpark version.
These functions are ported from newer versions of Spark to provide compatibility.
"""

from pyspark import SparkContext
from pyspark.sql.column import Column, _to_java_column, _to_seq, _create_column_from_literal


__all__ = ["percentile_approx", "array_repeat", "repeat"]


def percentile_approx(col, percentage, accuracy=10000):
    """
    Returns the approximate percentile value of numeric column col at the given percentage.
    
    Parameters
    ----------
    col : Column or str
        The column to calculate percentile on
    percentage : float, list, tuple, or Column
        The percentile(s) to calculate (must be between 0.0 and 1.0)
    accuracy : int or Column, default 10000
        Controls approximation accuracy at the cost of memory.
        Higher value yields better accuracy, 1.0/accuracy is the relative error.
    
    Returns
    -------
    Column
        The percentile value(s) as a Column
    
    Notes
    -----
    When percentage is an array, each value must be between 0.0 and 1.0.
    In this case, returns the approximate percentile array at the given percentage array.
    
    Ported from Spark 3.1.
    """
    sc = SparkContext._active_spark_context

    # Process percentage parameter based on its type
    if isinstance(percentage, (list, tuple)):
        # Convert list of percentages to a Spark array
        percentage = sc._jvm.functions.array(
            _to_seq(sc, [_create_column_from_literal(x) for x in percentage])
        )
    elif isinstance(percentage, Column):
        # Already a Column, convert to Java column
        percentage = _to_java_column(percentage)
    else:
        # Scalar value, convert to literal column
        percentage = _create_column_from_literal(percentage)

    # Process accuracy parameter
    accuracy = (
        _to_java_column(accuracy)
        if isinstance(accuracy, Column)
        else _create_column_from_literal(accuracy)
    )

    # Call the UDF with properly prepared arguments
    return _call_udf(sc, "percentile_approx", _to_java_column(col), percentage, accuracy)


def array_repeat(col, count):
    """
    Collection function: creates an array containing a column repeated count times.
    
    Parameters
    ----------
    col : Column or str
        The column to repeat
    count : int or Column
        Number of times to repeat the column
    
    Returns
    -------
    Column
        Array column containing the repeated value
    
    Notes
    -----
    Ported from Spark 3.0.
    """
    sc = SparkContext._active_spark_context
    
    # Convert count to Java format if it's a Column
    java_count = _to_java_column(count) if isinstance(count, Column) else count
    
    return Column(
        sc._jvm.functions.array_repeat(_to_java_column(col), java_count)
    )


def repeat(col, n):
    """
    Repeats a string column n times, and returns it as a new string column.
    
    Parameters
    ----------
    col : Column or str
        The string column to repeat
    n : int or Column
        Number of times to repeat the string
    
    Returns
    -------
    Column
        String column with repeated content
    """
    sc = SparkContext._active_spark_context
    
    # Convert n to appropriate format
    java_n = _to_java_column(n) if isinstance(n, Column) else _create_column_from_literal(n)
    
    return _call_udf(sc, "repeat", _to_java_column(col), java_n)


def _call_udf(sc, name, *cols):
    """
    Helper function to call a Spark UDF with the given name and columns.
    
    Parameters
    ----------
    sc : SparkContext
        Active Spark context
    name : str
        Name of the UDF to call
    *cols : list of Column
        Arguments to pass to the UDF
    
    Returns
    -------
    Column
        Result of the UDF call
    """
    return Column(sc._jvm.functions.callUDF(name, _make_arguments(sc, *cols)))


def _make_arguments(sc, *cols):
    """
    Helper function to convert Python columns to a Java array of columns.
    
    Parameters
    ----------
    sc : SparkContext
        Active Spark context
    *cols : list of Column
        Columns to convert
    
    Returns
    -------
    JavaArray
        Java array containing the converted columns
    """
    # Create a new Java array of Column type with the specified length
    java_arr = sc._gateway.new_array(sc._jvm.Column, len(cols))
    
    # Populate the array with Java column objects
    for i, col in enumerate(cols):
        java_arr[i] = col
        
    return java_arr