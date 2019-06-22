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

import time
import requests
import sites

current.environment = "test"
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"

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
                    "tags": [u'Dynamic Programming', u'Mathematics', u'Medium', u'Number Theory']
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
                "CodeForces": "http://www.codeforces.com/problemset/gymProblem/100570/C",
                "Spoj": "https://www.spoj.com/problems/TOUR/",
                "HackerEarth": "https://www.hackerearth.com/problem/algorithm/find-pairs-1/",
                "Timus": "http://acm.timus.ru/problem.aspx?space=1&num=1559&locale=en"
            }
        }


        for site in sites_with_tags_functionality:
            P = self.profile_site[site]

            if P.is_website_down():
                # Don't test for websites which are acked to be down
                continue

            tags_func = P.get_tags
            tags_val = tags_func(assertion_hash["with_tags"][site]["plink"])
            if set(tags_val) != set(assertion_hash["with_tags"][site]["tags"]):
                raise RuntimeError(site + " with tags failure")

            if site in assertion_hash["without_tags"]:
                tags_val = tags_func(assertion_hash["without_tags"][site])
                if tags_val not in ([u"-"], []):
                    raise RuntimeError(site + " without tags failure")

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
                "CodeForces": "http://www.codeforces.com/problemset/problem/234/D"
            }
        }
        for site in sites_with_editorial_functionality:
            P = self.profile_site[site]

            if P.is_website_down():
                # Don't test for websites which are acked to be down
                continue

            editorial_func = P.get_editorial_link
            editorial_link = editorial_func(assertion_hash["with_editorial"][site]["plink"])
            if editorial_link != assertion_hash["with_editorial"][site]["editorial_link"]:
                raise RuntimeError(site + " with editorial failure")

            if site in assertion_hash["without_editorial"]:
                editorial_link = editorial_func(assertion_hash["without_editorial"][site])
                if editorial_link is not None:
                    raise RuntimeError(site + " without editorial failure")

    # --------------------------------------------------------------------------
    def test_invalid_handle(self):
        handle = "thisreallycantbeahandle308"
        result = map(lambda site: (site, self.profile_site[site].is_invalid_handle(handle)),
                     filter(lambda site: self.profile_site[site].is_website_down() == False,
                            current.SITES.keys()))
        failure_sites = []
        for site, res in result:
            if not res:
                failure_sites.append(site)

        if len(failure_sites) > 0:
            raise RuntimeError(", ".join(failure_sites) + " " + "invalid handle failure")

    # --------------------------------------------------------------------------
    def test_download_submission(self):
        import requests
        from bs4 import BeautifulSoup

        sites_with_download_functionality = ["CodeChef", "CodeForces"]
        assertion_hash = {
            "CodeChef": {
                "view_link": "https://www.codechef.com/viewsolution/4530125",
                "submission": '#include<stdio.h>\n#include<math.h>\n#include<string.h>\n#define g getchar_unlocked\nint prime[10000];\nint notprime[100000]={0};\nint z=0,i,j;\nint readnum()\n{\n\tint n=0;\n\tchar c=g();\n\twhile(c<\'0\'||c>\'9\')c=g();\n\twhile(c>=\'0\'&&c<=\'9\')n=10*n+c-\'0\',c=g();\n\treturn n;\n}\ninline void fastWrite(int a)\n{\n\tchar snum[20];\n\tint i=0;\n\tdo\n\t{\n\t\tsnum[i++]=a+48;\n\t\ta=a/10;\n\t}while(a!=0);\n\ti=i-1;\n\twhile(i>=0)\n\t\tputchar_unlocked(snum[i--]);\n\tputchar_unlocked(\'\\n\');\n}\nvoid seive()\n{\n\tnotprime[0]=1;\n\tnotprime[1]=1;\n\tfor(i=2;i<100000;i++)\n\t{\n\t\tif(notprime[i]==0)\n\t\t{\n\t\t\tprime[z++]=i;\n\t\t\tfor(j=i+i;j<100000;j+=i)\n\t\t\t\tnotprime[j]=1;\n\t\t}\n\t}\n\t \n}\nint main()\n{\n\tseive();\n\t/* for(i=0;i<1000;i++)\n\t   printf("%d ",prime[i]);\n\t   */\tint m,n,t,i,sq,flag;\n\t//scanf("%d",&t);\n\tt=readnum();\n\twhile(t--)\n\t{\n\t\t//scanf("%d%d",&m,&n);\n\t\tm=readnum();\n\t\tn=readnum();\n\t\tif(m<=2)\n\t\t{\n\t\t\tprintf("2\\n");\n\t\t\tm=3;\n\t\t}\n\t\telse if(m%2==0)\n\t\t\tm=m+1;\n\t\tfor(i=m;i<=n;i+=2)\n\t\t{\n\t\t\tflag=0;\n\t\t\tsq=sqrt(i);\n\t\t\tfor(j=1;prime[j]<=sq;j++)\n\t\t\t{\n\t\t\t\tif(i%prime[j]==0)\n\t\t\t\t{\n\t\t\t\t\tflag=1;\n\t\t\t\t\tbreak;\n\t\t\t\t}\n\t\t\t}\n\t\t\tif(flag==0)\n\t\t\t\tfastWrite(i);\n\t\t}\n\t}\n\treturn 0;\n}\n'
            },
            "CodeForces": {
                "view_link": "http://www.codeforces.com/contest/454/submission/7375767",
                "submission": '#include<stdio.h>\nint main()\n{\n\tint n,i,j,k;\n\tscanf("%d",&n);\n\tint h=n/2+1;\n\tfor(i=0;i<h;i++)\n\t{\n\t\tfor(k=0;k<n/2-i;k++)\n\t\t\tprintf("*");\n\t\tfor(j=0;j<2*i+1;j++)\n\t\t\tprintf("D");\n\t\tfor(j=n/2+i+1;j<n;j++)\n\t\t\tprintf("*");\n\t\tprintf("\\n");\n\t}\n\tfor(i=0;i<n/2;i++)\n\t{\n\t\tfor(k=0;k<=i;k++)\n\t\t        printf("*");\n\t\tfor(j=n-2*i;j>=3;j--)\n\t\t\tprintf("D");\n\t\tfor(j=0;j<=i;j++)\n\t\t\tprintf("*");\n\t\tprintf("\\n");\n\t}\n\treturn 0;\n}\n'
            }
        }

        for site in sites_with_download_functionality:
            P = self.profile_site[site]

            if P.is_website_down():
                # Don't test for websites which are acked to be down
                continue

            submission_content = P.download_submission(assertion_hash[site]["view_link"])
            if submission_content != assertion_hash[site]["submission"]:
                raise RuntimeError(site + " download submission failed")

    # --------------------------------------------------------------------------
    def test_rating_graph(self):
        sites_with_rating_graph_functionality = ["CodeChef", "CodeForces", "HackerRank", "HackerEarth"]
        handles = {
            "CodeChef": "tryingtocode",
            "CodeForces": "raj454raj",
            "HackerRank": "tryingtocode",
            "HackerEarth": "karanaggarwal"
        }
        expected_list = [['2014-01-13 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/JAN14', 'rating': '1462', 'name': 'January Challenge 2014', 'rank': '3548'}], ['2014-02-17 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/FEB14', 'rating': '1509', 'name': 'February Challenge 2014', 'rank': '2007'}], ['2014-06-16 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/JUNE14', 'rating': '1455', 'name': 'June Challenge 2014', 'rank': '4382'}], ['2014-07-14 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/JULY14', 'rating': '1518', 'name': 'July Challenge 2014', 'rank': '2769'}], ['2014-07-21 21:30:00', u'HackerRank - Algorithms', {'url': u'https://www.hackerrank.com/w7', 'rating': '1554.46', 'name': u'Weekly Challenges - Week 7', 'rank': 499}], ['2014-08-08 21:00:00', 'Codeforces', {'rating': '1403', 'name': u'Codeforces Round #260 (Div. 2)', 'solvedCount': 0, 'url': 'http://www.codeforces.com/contest/456', 'rank': 2152, 'ratingChange': -97}], ['2014-08-11 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/AUG14', 'rating': '1633', 'name': 'August Challenge 2014', 'rank': '1293'}], ['2014-08-11 21:30:00', u'HackerRank - Algorithms', {'url': u'https://www.hackerrank.com/w8', 'rating': '1276.88', 'name': u'Weekly Challenges - Week 8', 'rank': 1204}], ['2014-09-28 21:05:00', 'Codeforces', {'rating': '1279', 'name': u'Codeforces Round #270', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/472', 'rank': 3520, 'ratingChange': -124}], ['2014-10-06 21:00:00', 'Codeforces', {'rating': '1227', 'name': u'Codeforces Round #271 (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/474', 'rank': 1654, 'ratingChange': -52}], ['2014-10-13 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/OCT14', 'rating': '1730', 'name': 'October Challenge 2014', 'rank': '900'}], ['2014-11-17 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/NOV14', 'rating': '1717', 'name': 'November Challenge 2014', 'rank': '1751'}], ['2014-12-15 17:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/DEC14', 'rating': '1609', 'name': 'December Challenge 2014', 'rank': '2218'}], ['2015-01-12 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/JAN15', 'rating': '1617', 'name': 'January Challenge 2015', 'rank': '3105'}], ['2015-03-16 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/MARCH15', 'rating': '1553', 'name': 'March Challenge 2015', 'rank': '2489'}], ['2015-05-18 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/MAY15', 'rating': '1519', 'name': 'May Challenge 2015', 'rank': '2946'}], ['2015-06-15 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/JUNE15', 'rating': '1605', 'name': 'June Challenge 2015', 'rank': '1913'}], ['2015-07-13 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/JULY15', 'rating': '1635', 'name': 'July Challenge 2015', 'rank': '1554'}], ['2015-08-02 21:30:00', u'HackerRank - Algorithms', {'url': u'https://www.hackerrank.com/countercode', 'rating': '1287.0', 'name': u'CounterCode 2015', 'rank': 3605}], ['2015-08-17 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/AUG15', 'rating': '1704', 'name': 'August Challenge 2015', 'rank': '1244'}], ['2015-08-22 22:00:00', 'Codeforces', {'rating': '1358', 'name': u'Codeforces Round #317 [AimFund Thanks-Round] (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/572', 'rank': 1114, 'ratingChange': 131}], ['2015-08-24 00:50:00', 'CodeChef Cook-off', {'url': 'https://www.codechef.com/COOK61', 'rating': '1881', 'name': 'August Cook-Off 2015', 'rank': '221'}], ['2015-08-29 22:00:00', 'Codeforces', {'rating': '1288', 'name': u'Codeforces Round #318 [RussianCodeCup Thanks-Round] (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/574', 'rank': 2009, 'ratingChange': -70}], ['2015-09-10 22:00:00', 'Codeforces', {'rating': '1422', 'name': u'Codeforces Round #319 (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/577', 'rank': 940, 'ratingChange': 134}], ['2015-09-14 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/SEPT15', 'rating': '1829', 'name': 'September Challenge 2015', 'rank': '1417'}], ['2015-09-21 00:00:00', 'CodeChef Cook-off', {'url': 'https://www.codechef.com/COOK62', 'rating': '1807', 'name': 'September Mega Cook-Off 2015', 'rank': '751'}], ['2015-09-22 22:00:00', 'Codeforces', {'rating': '1379', 'name': u'Codeforces Round #321 (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/580', 'rank': 2018, 'ratingChange': -43}], ['2015-09-28 14:30:00', 'Codeforces', {'rating': '1295', 'name': u'Codeforces Round #322 (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/581', 'rank': 1836, 'ratingChange': -84}], ['2015-10-03 22:15:00', 'Codeforces', {'rating': '1285', 'name': u'Codeforces Round #323 (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/583', 'rank': 2912, 'ratingChange': -10}], ['2015-10-06 22:00:00', 'Codeforces', {'rating': '1298', 'name': u'Codeforces Round #324 (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/584', 'rank': 2062, 'ratingChange': 13}], ['2015-10-25 14:30:00', 'Codeforces', {'rating': '1273', 'name': u'Codeforces Round #327 (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/591', 'rank': 2259, 'ratingChange': -25}], ['2015-10-30 21:30:00', u'HackerRank - Algorithms', {'url': u'https://www.hackerrank.com/codestorm', 'rating': '1276.05', 'name': u'CodeStorm 2015', 'rank': 3743}], ['2015-10-31 22:00:00', 'Codeforces', {'rating': '1284', 'name': u'Codeforces Round #328 (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/592', 'rank': 2075, 'ratingChange': 11}], ['2015-12-01 21:05:00', 'Codeforces', {'rating': '1351', 'name': u'Codeforces Round #334 (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/604', 'rank': 1079, 'ratingChange': 67}], ['2015-12-09 21:35:00', 'Codeforces', {'rating': '1309', 'name': u'Codeforces Round #335 (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/606', 'rank': 2249, 'ratingChange': -42}], ['2016-01-14 22:05:00', 'Codeforces', {'rating': '1228', 'name': u'Codeforces Round #339 (Div. 2)', 'solvedCount': 0, 'url': 'http://www.codeforces.com/contest/614', 'rank': 1929, 'ratingChange': -81}], ['2016-05-21 10:30:00', 'HackerEarth', {'url': 'https://www.hackerearth.com/challenges/competitive/may-circuits/', 'rating': 1493, 'name': 'May Circuits', 'rank': 714}], ['2016-06-15 15:00:00', 'CodeChef Long', {'url': 'https://www.codechef.com/JUNE16', 'rating': '1641', 'name': 'June Challenge 2016', 'rank': '5083'}], ['2016-08-11 22:05:00', 'Codeforces', {'rating': '1216', 'name': u'Codeforces Round #367 (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/706', 'rank': 2989, 'ratingChange': -12}], ['2016-08-20 18:35:00', 'Codeforces', {'rating': '1298', 'name': u'Codeforces Round #368 (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/707', 'rank': 1919, 'ratingChange': 82}], ['2016-08-29 17:35:00', 'Codeforces', {'rating': '1309', 'name': u'Codeforces Round #369 (Div. 2)', 'solvedCount': 1, 'url': 'http://www.codeforces.com/contest/711', 'rank': 2332, 'ratingChange': 11}], ['2016-09-23 18:35:00', 'Codeforces', {'rating': '1377', 'name': u'Codeforces Round #373 (Div. 2)', 'solvedCount': 2, 'url': 'http://www.codeforces.com/contest/719', 'rank': 1593, 'ratingChange': 68}], ['2017-07-28 10:30:00', 'HackerEarth', {'url': 'https://www.hackerearth.com/challenges/competitive/july-circuits-17/', 'rating': 1462, 'name': "July Circuits '17", 'rank': 1326}], ['2017-09-22 10:30:00', 'HackerEarth', {'url': 'https://www.hackerearth.com/challenges/competitive/september-circuits-17/', 'rating': 1569, 'name': "September Circuits '17", 'rank': 291}], ['2017-10-21 10:30:00', 'HackerEarth', {'url': 'https://www.hackerearth.com/challenges/competitive/october-circuits-17/', 'rating': 1491, 'name': "October Circuits '17", 'rank': 1225}], ['2018-03-17 10:30:00', 'HackerEarth', {'url': 'https://www.hackerearth.com/challenges/competitive/march-circuits-18/', 'rating': 1461, 'name': "March Circuits '18", 'rank': 523}], ['2019-01-18 09:30:00', 'HackerEarth', {'url': 'https://www.hackerearth.com/challenges/competitive/january-circuits-19/', 'rating': 1337, 'name': "January Circuits '19", 'rank': 3420}]]
        result = {}
        for site in sites_with_rating_graph_functionality:
            get_rating_func = getattr(sites, site.lower()).Profile.rating_graph_data
            res = get_rating_func(handles[site])
            result[site.lower() + "_data"] = res

        all_contest_points = []
        for site_data in result:
            for contest_data in result[site_data]:
                for data_point in contest_data["data"]:
                    all_contest_points.append([
                        data_point,
                        contest_data["title"],
                        contest_data["data"][data_point]
                    ])

        if sorted(all_contest_points, key=lambda x: x[0]) != expected_list:
            raise RuntimeError("Rating graph dict does not match")

# ------------------------------------------------------------------------------
def test_retrieval(retrieval_object, method_name):
    error_message = ""
    for i in xrange(5):
        try:
            getattr(retrieval_object, method_name)()
            return "Success"
        except Exception as e:
            error_message = e.message
        time.sleep(2)

    return error_message

rt = RetrievalTest()
pushover_message = ""

for method_name in ["test_tag_retrieval",
                    "test_editorial_retrieval",
                    "test_invalid_handle",
                    "test_download_submission",
                    "test_rating_graph"]:
    res = test_retrieval(rt, method_name)
    if res != "Success":
        pushover_message += res + "\n"

if pushover_message != "":
    print pushover_message
    response = requests.post("https://api.pushover.net/1/messages.json",
                             data={"token": current.pushover_api_token,
                                   "user": current.pushover_user_token,
                                   "message": pushover_message.strip(),
                                   "title": "Extras retrieval failure",
                                   "priority": 1}).json()
