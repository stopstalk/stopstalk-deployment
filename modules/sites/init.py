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

import re, requests, ast, time
import parsedatetime as pdt
import urllib3
import datetime
import bs4
import utilities
from gluon import current
from bs4 import BeautifulSoup
from health_metrics import MetricHandler
from stopstalk_constants import *

urllib3.disable_warnings()

# -----------------------------------------------------------------------------
def log_time_things(request_time_metric_handler, start_request_time, site):
    time_difference = time.time() - start_request_time
    request_time_metric_handler.add_to_list("list", time_difference)
    utilities.push_influx_data("crawling_response_times",
                               dict(kind="general_for_now",
                                    site=site,
                                    value=time_difference))

# -----------------------------------------------------------------------------
def get_request(url,
                headers={},
                timeout=current.TIMEOUT,
                params={},
                cookies={},
                is_daily_retrieval=False):
    """
        Make a HTTP GET request to a url

        @param url (String): URL to make get request to
        @param headers (Dict): Headers to be passed along
                               with the request headers
        @param timeout (Number): Number of seconds after which client will close
                                 the request
        @param params (Dict): Dictionary of get request parms
        @param cookies (Dict): Dictionary of cookies for the http request
        @param is_daily_retrieval (Boolean): Consider the function call to get_request
                                      for health report or not

        @return: Response object or one of REQUEST_FAILURES
    """

    if current.environment == "test":
        timeout = 20

    site = utilities.urltosite(url).lower()
    request_metric_handler = MetricHandler("request_stats",
                                           "success_failure",
                                           site,
                                           is_daily_retrieval)
    request_time_metric_handler = MetricHandler("request_times",
                                                "average",
                                                site,
                                                is_daily_retrieval)

    headers.update({"User-Agent": COMMON_USER_AGENT})

    i = 0
    while i < current.MAX_TRIES_ALLOWED:
        try:
            start_request_time = time.time()
            response = requests.get(url,
                                    headers=headers,
                                    params=params,
                                    proxies=current.PROXY,
                                    timeout=timeout,
                                    cookies=cookies,
                                    verify=False)
        except Exception as e:
            print(e, url)
            request_metric_handler.increment_count("failure", 1)
            log_time_things(request_time_metric_handler, start_request_time, site)
            return SERVER_FAILURE

        if response.status_code == 200:
            log_time_things(request_time_metric_handler, start_request_time, site)
            request_metric_handler.increment_count("success", 1)
            return response
        elif response.status_code == 404 or response.status_code == 400:
            log_time_things(request_time_metric_handler, start_request_time, site)
            # User not found
            # 400 for CodeForces users
            return NOT_FOUND
        elif response.status_code == 429 or response.status_code == 401:
            log_time_things(request_time_metric_handler, start_request_time, site)
            request_metric_handler.increment_count("failure", 1)
            # For CodeChef API rate limiting, don't retry
            # 401 is raised when a newer access token is generated
            print(response.status_code)
            if url.__contains__("codechef.com") and response.status_code == 401:
                current.REDIS_CLIENT.delete("codechef_access_token")
            return OTHER_FAILURE
        else:
            log_time_things(request_time_metric_handler, start_request_time, site)
            request_metric_handler.increment_count("failure", 1)

        i += 1

    # Request unsuccessful even after MAX_TRIES_ALLOWED
    return OTHER_FAILURE
