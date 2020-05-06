STOPSTALK_ADMIN_USER_IDS = [1]
JSON_DUMP_SEPARATORS = (",", ":")

INFLUX_DBNAME = "stopstalk_influxdb"
INFLUX_RETENTION_POLICY = "quarter"

INFLUX_MEASUREMENT_SCHEMAS = {
    "retrieval_stats": {
        "fields": ["value"],
        "tags": ["app_name", "host", "kind", "stopstalk_handle", "retrieval_type", "site"]
    },
    "crawling_response_times": {
        "fields": ["value"],
        "tags": ["app_name", "host", "site", "kind"]
    }
}

CODEFORCES_PROBLEM_SETTERS_KEY = "codeforces_problem_setters"

GLOBALLY_TRENDING_PROBLEMS_CACHE_KEY = "global_trending_table_cache"

CARD_REDIS_CACHE_TTL = 1 * 60 * 60

ADD_MORE_FRIENDS_REDIS_KEY_PREFIX = "cards::add_more_friends_cache_"

JOB_PROFILE_REDIS_KEY_PREFIX = "cards::job_profile_"