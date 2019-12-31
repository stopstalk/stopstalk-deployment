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

from gluon import current

kind_mapping = {
    "just_count": ["total"],
    "success_failure": ["success", "failure"],
    "average": ["list"]
}

# ==============================================================================
def get_redis_int_value(key_name):
    value = current.REDIS_CLIENT.get(key_name)
    return 0 if value is None else int(value)

# ==============================================================================
class MetricHandler(object):

    # --------------------------------------------------------------------------
    def __init__(self, genre, kind, site, log_to_redis):
        """
            Constructor for a specific MetricHandler

            @param genre (String): Metric identifier
            @param kind (String): Metric type ("just_count" or "success_failure")
            @param site (String): Metric handler is for which site
            @param log_to_redis (Boolean): If need to add it to redis
        """

        self.redis_client = current.REDIS_CLIENT

        # Kind of tracking that we need to do
        self.genre = genre
        # The label to print in the health report
        self.label = " ".join([x.capitalize() for x in self.genre.split("_")])
        # Just count or percentage
        self.kind = kind
        # Submission site
        self.site = site

        # If there metrics need to be persisted in redis
        self.log_to_redis = log_to_redis
        # The redis keys which will be used
        self.redis_keys = {}

        for type_of_key in kind_mapping[self.kind]:
            self.redis_keys[type_of_key] = "health_metrics:%s__%s__%s" % (self.genre,
                                                                          self.site,
                                                                          type_of_key)

    # --------------------------------------------------------------------------
    def flush_keys(self):
        """
            Remove all the keys for this MetricHandler from redis
        """
        if self.log_to_redis is False:
            return

        [self.redis_client.delete(key) for key in self.redis_keys.values()]

    # --------------------------------------------------------------------------
    def increment_count(self, type_of_key, increment_amount=1):
        """
            Increment count of a metric given success key or failure key

            @param type_of_key (String): "success" or "failure"
            @param increment_amount (Number): Amount by which the redis key
                                              should be incremented
        """
        if self.log_to_redis is False:
            return

        redis_key = self.redis_keys[type_of_key]
        value = self.redis_client.get(redis_key)
        if value is None:
            value = 0
        else:
            value = int(value)

        self.redis_client.set(redis_key, value + increment_amount)

    # --------------------------------------------------------------------------
    def add_to_list(self, type_of_key, value):
        """
            Add a value to the list for computing average later

            @param value (Decimal): A decimal to be added to the list
            @param type_of_key (String): At present just "list"
        """
        if self.log_to_redis is False:
            return

        self.redis_client.lpush(self.redis_keys[type_of_key], value)

    # --------------------------------------------------------------------------
    def _get_average_string(self):
        all_values = self.redis_client.lrange(self.redis_keys["list"], 0, -1)
        return_str = None
        if len(all_values):
            all_values = [float(x) for x in all_values]
            average = sum(all_values) * 1.0 / len(all_values)
            return_str = str(average)
        else:
            return_str = "-"
        return return_str

    # --------------------------------------------------------------------------
    def get_html(self):
        html_body = "<tr><td style='background-color: lavender;'><b>%s</b></td>" % self.label
        if self.kind == "just_count":
            html_body += "<td colspan='3'>Total: %d</td>" % get_redis_int_value(self.redis_keys["total"])
        elif self.kind == "success_failure":
            success = get_redis_int_value(self.redis_keys["success"])
            failure = get_redis_int_value(self.redis_keys["failure"])
            if failure > 0:
                failure_percentage = str(failure * 100.0 / (failure + success))
            else:
                failure_percentage = "-"
            html_body += """
<td>Success: %d</td><td>Failure: %d</td><td>Failure per: %s</td>
            """ % (success,
                   failure,
                   failure_percentage)
        elif self.kind == "average":
            html_body += "<td colspan='3'>Average: %s</td>" % self._get_average_string()
        else:
            html_body += "<td colspane='3'>Unknown kind</td>"
        html_body += "</tr>"
        return html_body

    # --------------------------------------------------------------------------
    def __str__(self):
        """
            Representation of the MetricHandler
        """
        return_str = self.label + ": "
        if self.kind == "just_count":
            return_str += str(get_redis_int_value(self.redis_keys["total"]))
        elif self.kind == "success_failure":
            return_str += str(get_redis_int_value(self.redis_keys["success"])) + " " + \
                          str(get_redis_int_value(self.redis_keys["failure"]))
        elif self.kind == "average":
            return_str += self._get_average_string()

        return return_str

