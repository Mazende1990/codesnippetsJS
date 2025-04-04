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
Additional Spark functions for Koalas.
"""

from pyspark import SparkContext
from pyspark.sql.column import Column, _to_java_column, _to_seq, _create_column_from_literal

__all__ = ["percentile_approx"]


def percentile_approx(col, percentage, accuracy=10000):
    """
    Calculates the approximate percentile value of a numeric column.

    Args:
        col (Column): The numeric column to calculate the percentile for.
        percentage (float or list or Column): The percentile(s) to calculate. Must be between 0.0 and 1.0.
            If a list, returns an array of percentiles.
        accuracy (int or Column): The approximation accuracy. Higher values yield better accuracy at the cost of memory.
            Defaults to 10000.

    Returns:
        Column: The approximate percentile value or array of percentile values.

    Ported from Spark 3.1.
    """
    sc = SparkContext._active_spark_context

    if isinstance(percentage, (list, tuple)):
        percentage = sc._jvm.functions.array(
            _to_seq(sc, [_create_column_from_literal(x) for x in percentage])
        )
    elif isinstance(percentage, Column):
        percentage = _to_java_column(percentage)
    else:
        percentage = _create_column_from_literal(percentage)

    accuracy = (
        _to_java_column(accuracy)
        if isinstance(accuracy, Column)
        else _create_column_from_literal(accuracy)
    )

    return _call_udf(sc, "percentile_approx", _to_java_column(col), percentage, accuracy)


def array_repeat(col, count):
    """
    Creates an array containing a column repeated a specified number of times.

    Args:
        col (Column): The column to repeat.
        count (int or Column): The number of times to repeat the column.

    Returns:
        Column: The array containing the repeated column.

    Ported from Spark 3.0.
    """
    sc = SparkContext._active_spark_context
    return Column(
        sc._jvm.functions.array_repeat(
            _to_java_column(col), _to_java_column(count) if isinstance(count, Column) else count
        )
    )


def repeat(col, n):
    """
    Repeats a string column n times.

    Args:
        col (Column): The string column to repeat.
        n (int or Column): The number of times to repeat the string.

    Returns:
        Column: The new string column with repeated values.
    """
    sc = SparkContext._active_spark_context
    n = _to_java_column(n) if isinstance(n, Column) else _create_column_from_literal(n)
    return _call_udf(sc, "repeat", _to_java_column(col), n)


def _call_udf(sc, name, *cols):
    """
    Calls a user-defined function (UDF) in Spark.

    Args:
        sc (SparkContext): The active SparkContext.
        name (str): The name of the UDF.
        *cols (Column): The columns to pass as arguments to the UDF.

    Returns:
        Column: The result of the UDF call as a Column.
    """
    return Column(sc._jvm.functions.callUDF(name, _make_arguments(sc, *cols)))


def _make_arguments(sc, *cols):
    """
    Creates a Java array of Column objects.

    Args:
        sc (SparkContext): The active SparkContext.
        *cols (Column): The Column objects to include in the array.

    Returns:
        Java array of Column objects.
    """
    java_arr = sc._gateway.new_array(sc._jvm.Column, len(cols))
    for i, col in enumerate(cols):
        java_arr[i] = col
    return java_arr