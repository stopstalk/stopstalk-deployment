"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

from influxdb import SeriesHelper
from gluon import current

series_helper_classes = {}

# ------------------------------------------------------------------------------
def get_series_helper(measurement_name,
                      measurement_fields,
                      measurement_tags):
    if measurement_name in series_helper_classes:
        return series_helper_classes[measurement_name]
    else:
        series_helper_classes[measurement_name] = series_helper_class_wrapper(
            measurement_name,
            measurement_fields,
            measurement_tags
        )
        return series_helper_classes[measurement_name]

# ------------------------------------------------------------------------------
def series_helper_class_wrapper(measurement_name,
                                measurement_fields,
                                measurement_tags):

    class StopStalkSeriesHelper(SeriesHelper):
        """Instantiate SeriesHelper to write points to the backend."""

        class Meta:
            """Meta class stores time series helper configuration."""

            # The client should be an instance of InfluxDBClient.
            client = current.INFLUXDB_CLIENT

            # The series name must be a string. Add dependent fields/tags
            # in curly brackets.
            series_name = measurement_name

            # Defines all the fields in this time series.
            fields = measurement_fields

            # Defines all the tags for the series.
            tags = measurement_tags

            # Defines the number of data points to store prior to writing
            # on the wire.
            bulk_size = 5

            # autocommit must be set to True when using bulk_size
            autocommit = True

    return StopStalkSeriesHelper