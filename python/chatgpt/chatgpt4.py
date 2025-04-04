# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------

"""
Additional Spark functions used in Koalas.
"""

from pyspark import SparkContext
from pyspark.sql.column import (
    Column,
    _to_java_column,
    _to_seq,
    _create_column_from_literal,
)


__all__ = ["percentile_approx"]


def percentile_approx(col, percentage, accuracy=10000):
    """
    Returns the approximate percentile value of a numeric column at a given percentage.

    Parameters:
        col (Column): The numeric column.
        percentage (float, list, or Column): A value or array between 0.0 and 1.0.
        accuracy (int or Column): Approximation accuracy. Higher values yield better results.

    Returns:
        Column: Approximate percentile(s) as a new column.

    Notes:
        - If `percentage` is a list or tuple, returns a column with approximate percentiles.
        - Ported from Apache Spark 3.1.
    """
    sc = SparkContext._active_spark_context

    if isinstance(percentage, (list, tuple)):
        percentage = sc._jvm.functions.array(
            _to_seq(sc, [_create_column_from_literal(p) for p in percentage])
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
    Creates an array containing a column repeated `count` times.

    Parameters:
        col (Column): The value to repeat.
        count (int or Column): The number of repetitions.

    Returns:
        Column: A new array column with repeated values.

    Notes:
        - Ported from Apache Spark 3.0.
    """
    sc = SparkContext._active_spark_context
    count_java = _to_java_column(count) if isinstance(count, Column) else count

    return Column(sc._jvm.functions.array_repeat(_to_java_column(col), count_java))


def repeat(col, n):
    """
    Repeats the value of a string column `n` times.

    Parameters:
        col (Column): String column to repeat.
        n (int or Column): Number of repetitions.

    Returns:
        Column: New string column with repeated values.
    """
    sc = SparkContext._active_spark_context
    n = _to_java_column(n) if isinstance(n, Column) else _create_column_from_literal(n)

    return _call_udf(sc, "repeat", _to_java_column(col), n)


def _call_udf(sc, name, *cols):
    """
    Helper function to call a registered Spark UDF with Java columns.
    """
    return Column(sc._jvm.functions.callUDF(name, _make_arguments(sc, *cols)))


def _make_arguments(sc, *cols):
    """
    Creates a Java array of Spark Column objects.
    """
    java_arr = sc._gateway.new_array(sc._jvm.Column, len(cols))
    for i, col in enumerate(cols):
        java_arr[i] = col
    return java_arr
