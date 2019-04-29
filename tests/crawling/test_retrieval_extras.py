"""
    Copyright (c) 2015-2019 Raj Patel(raj454raj@gmail.com), StopStalk

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

import sites

current.environment = "test"

# ==============================================================================
class RetrievalTest:

    # --------------------------------------------------------------------------
    def __init__(self):
        self.profile_site = {}
        for site in current.SITES:
            self.profile_site[site] = getattr(sites, site.lower()).Profile

    # --------------------------------------------------------------------------
    def test_tag_retrieval(self):
        sites_with_tags_functionality = ["CodeChef", "CodeForces", "Spoj", "HackerEarth", "HackerRank", "Timus"]
        assertion_hash = {
            "with_tags": {
                "CodeChef": {
                    "plink": "https://www.codechef.com/PRACTICE/problems/FNCS",
                    "tags": [u'data-structure', u'devuy11', u'fenwick', u'medium-hard', u'nov14', u'segment-tree', u'sqrt-decomp']
                },
                "CodeForces": {
                    "plink": "http://www.codeforces.com/problemset/problem/323/A",
                    "tags": [u'combinatorics', u'constructive algorithms', u'*1600']
                },
                "Spoj": {
                    "plink": "https://www.spoj.com/problems/YODANESS/",
                    "tags": [u'graph-theory', u'number-theory', u'shortest-path', u'sorting', u'tree', u'bitmasks']
                },
                "HackerEarth": {
                    "plink": "https://www.hackerearth.com/practice/algorithms/dynamic-programming/2-dimensional/practice-problems/algorithm/candy-distribution/",
                    "tags": [u'Dynamic Programming', u'Medium', u'Number Theory']
                },
                "HackerRank": {
                    "plink": "https://www.hackerrank.com/challenges/print-the-elements-of-a-linked-list",
                    "tags": [u'Linked Lists']
                },
                "Timus": {
                    "plink": "http://acm.timus.ru/problem.aspx?space=1&num=1954&locale=en",
                    "tags": [u'hardest problem', u'palindromes', u'string algorithms']
                }
            },
            "without_tags": {
                "CodeChef": "https://www.codechef.com/ZCOPRAC/problems/ZCO14004",
                "CodeForces": "https://codeforces.com/problemset/gymProblem/100570/C",
                "Spoj": "https://www.spoj.com/problems/TOUR/",
                "HackerEarth": "https://www.hackerearth.com/problem/algorithm/find-pairs-1/",
                "Timus": "http://acm.timus.ru/problem.aspx?space=1&num=1559&locale=en"
            }
        }


        for site in sites_with_tags_functionality:
            tags_func = self.profile_site[site].get_tags
            tags_val = tags_func(assertion_hash["with_tags"][site]["plink"])
            assert(set(tags_val) == set(assertion_hash["with_tags"][site]["tags"]))

            if site in assertion_hash["without_tags"]:
                tags_val = tags_func(assertion_hash["without_tags"][site])
                assert(tags_val in ([u"-"], []))

    # --------------------------------------------------------------------------
    def test_editorial_retrieval(self):
        sites_with_editorial_functionality = ["CodeChef", "CodeForces", "HackerEarth", "HackerRank"]
        assertion_hash = {
            "with_editorial": {
                "CodeChef": {
                    "plink": "https://www.codechef.com/LTIME27/problems/INVERT",
                    "editorial_link": "http://discuss.codechef.com/problems/INVERT"
                },
                "CodeForces": {
                    "plink": "http://www.codeforces.com/problemset/problem/102/B",
                    "editorial_link": "http://www.codeforces.com/blog/entry/2393"
                },
                "HackerEarth": {
                    "plink": "https://www.hackerearth.com/problem/algorithm/level-selections/",
                    "editorial_link": "https://www.hackerearth.com/problem/algorithm/level-selections/editorial/"
                },
                "HackerRank": {
                    "plink": "https://www.hackerrank.com/challenges/candles-2",
                    "editorial_link": "https://www.hackerrank.com/challenges/candles-2/editorial/"
                }
            },
            "without_editorial": {
                "CodeChef": "https://www.codechef.com/PRACTICE/problems/PG",
                "CodeForces": "https://www.codeforces.com/problemset/problem/234/D"
            }
        }
        for site in sites_with_editorial_functionality:
            editorial_func = self.profile_site[site].get_editorial_link
            editorial_link = editorial_func(assertion_hash["with_editorial"][site]["plink"])
            assert(editorial_link == assertion_hash["with_editorial"][site]["editorial_link"])

            if site in assertion_hash["without_editorial"]:
                editorial_link = editorial_func(assertion_hash["without_editorial"][site])
                assert(editorial_link == None)

    # --------------------------------------------------------------------------
    def test_invalid_handle(self):
        handle = "thisreallycantbeahandle308"
        assert(all(map(lambda site: self.profile_site.is_invalid_handle(handle), current.SITES.keys())))

rt = RetrievalTest()
rt.test_tag_retrieval()
rt.test_editorial_retrieval()
rt.test_invalid_handle()

