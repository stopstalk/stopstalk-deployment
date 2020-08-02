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

ONE_HOUR = 1 * 60 * 60

CARD_CACHE_REDIS_KEYS = {
    "add_more_friends_prefix": "cards::add_more_friends_cache_",
    "job_profile_prefix": "cards::job_profile_cache_",
    "upcoming_contests": "cards::upcoming_contests",
    "recent_submissions_prefix": "cards::recent_submissions_cache_",
    "more_accounts_prefix": "cards::more_accounts_cache_",
    "last_solved_problem_prefix": "cards::last_solved_problem_cache_",
    "trending_problems": "cards::trending_problems",
    "search_by_tag": "cards::search_by_tag",
    "curr_streak_prefix": "cards::streak_cache_"
}

CONTESTS_CACHE_KEY = "upcoming_contests_cache"
GLOBAL_LEADERBOARD_CACHE_KEY = "global_leaderboard_cache"

CONTESTS_SITE_MAPPING = {"CODECHEF": "CodeChef",
                         "CODEFORCES": "Codeforces",
                         "HACKERRANK": "HackerRank",
                         "HACKEREARTH": "HackerEarth"}

COMMON_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"

# Constants to be used in case of request failures
SERVER_FAILURE = "SERVER_FAILURE"
NOT_FOUND = "NOT_FOUND"
OTHER_FAILURE = "OTHER_FAILURE"

REQUEST_FAILURES = (SERVER_FAILURE, NOT_FOUND, OTHER_FAILURE)

VIEW_ONLY_SUBMISSION_SITES = ["HackerEarth"]

# Constants for recommendations
PAST_PROBLEM_COUNT = 10
DIFFICULTY_RANGE = 0.5
RECOMMENDATION_COUNT = 10
RECOMMENDATION_REFRESH_INTERVAL = 7

RECOMMENDATION_STATUS = {
    "RECOMMENDED": 0,
    "VIEWED": 1,
    "ATTEMPTED": 2,
    "SOLVED": 3
}
