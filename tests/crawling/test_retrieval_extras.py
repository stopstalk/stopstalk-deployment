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
                "CodeForces": "https://www.codeforces.com/problemset/problem/234/D"
            }
        }
        for site in sites_with_editorial_functionality:
            editorial_func = self.profile_site[site].get_editorial_link
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
        result = map(lambda site: (site, self.profile_site[site].is_invalid_handle(handle)), current.SITES.keys())
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
                "submission": '#incldude<stdio.h>\n#include<math.h>\n#include<string.h>\n#define g getchar_unlocked\nint prime[10000];\nint notprime[100000]={0};\nint z=0,i,j;\nint readnum()\n{\n\tint n=0;\n\tchar c=g();\n\twhile(c<\'0\'||c>\'9\')c=g();\n\twhile(c>=\'0\'&&c<=\'9\')n=10*n+c-\'0\',c=g();\n\treturn n;\n}\ninline void fastWrite(int a)\n{\n\tchar snum[20];\n\tint i=0;\n\tdo\n\t{\n\t\tsnum[i++]=a+48;\n\t\ta=a/10;\n\t}while(a!=0);\n\ti=i-1;\n\twhile(i>=0)\n\t\tputchar_unlocked(snum[i--]);\n\tputchar_unlocked(\'\\n\');\n}\nvoid seive()\n{\n\tnotprime[0]=1;\n\tnotprime[1]=1;\n\tfor(i=2;i<100000;i++)\n\t{\n\t\tif(notprime[i]==0)\n\t\t{\n\t\t\tprime[z++]=i;\n\t\t\tfor(j=i+i;j<100000;j+=i)\n\t\t\t\tnotprime[j]=1;\n\t\t}\n\t}\n\t \n}\nint main()\n{\n\tseive();\n\t/* for(i=0;i<1000;i++)\n\t   printf("%d ",prime[i]);\n\t   */\tint m,n,t,i,sq,flag;\n\t//scanf("%d",&t);\n\tt=readnum();\n\twhile(t--)\n\t{\n\t\t//scanf("%d%d",&m,&n);\n\t\tm=readnum();\n\t\tn=readnum();\n\t\tif(m<=2)\n\t\t{\n\t\t\tprintf("2\\n");\n\t\t\tm=3;\n\t\t}\n\t\telse if(m%2==0)\n\t\t\tm=m+1;\n\t\tfor(i=m;i<=n;i+=2)\n\t\t{\n\t\t\tflag=0;\n\t\t\tsq=sqrt(i);\n\t\t\tfor(j=1;prime[j]<=sq;j++)\n\t\t\t{\n\t\t\t\tif(i%prime[j]==0)\n\t\t\t\t{\n\t\t\t\t\tflag=1;\n\t\t\t\t\tbreak;\n\t\t\t\t}\n\t\t\t}\n\t\t\tif(flag==0)\n\t\t\t\tfastWrite(i);\n\t\t}\n\t}\n\treturn 0;\n}\n'
            },
            "CodeForces": {
                "view_link": "http://www.codeforces.com/contest/454/submission/7375767",
                "submission": '#include<stdio.h>\nint main()\n{\n\tint n,i,j,k;\n\tscanf("%d",&n);\n\tint h=n/2+1;\n\tfor(i=0;i<h;i++)\n\t{\n\t\tfor(k=0;k<n/2-i;k++)\n\t\t\tprintf("*");\n\t\tfor(j=0;j<2*i+1;j++)\n\t\t\tprintf("D");\n\t\tfor(j=n/2+i+1;j<n;j++)\n\t\t\tprintf("*");\n\t\tprintf("\\n");\n\t}\n\tfor(i=0;i<n/2;i++)\n\t{\n\t\tfor(k=0;k<=i;k++)\n\t\t        printf("*");\n\t\tfor(j=n-2*i;j>=3;j--)\n\t\t\tprintf("D");\n\t\tfor(j=0;j<=i;j++)\n\t\t\tprintf("*");\n\t\tprintf("\\n");\n\t}\n\treturn 0;\n}\n'
            }
        }

        # Copied from https://github.com/stopstalk/stopstalk-deployment/blob/ac78cfcba4874fb1a5a6ac73112933fb0faa89c3/controllers/default.py#L1462
        def _response_handler(download_url, response):
            return BeautifulSoup(response.text, "lxml").find("pre").text

        def _retrieve_codechef_submission(view_link):
            problem_id = view_link.strip("/").split("/")[-1]
            download_url = "https://www.codechef.com/viewplaintext/" + \
                           str(problem_id)
            response = requests.get(download_url,
                                    headers={"User-Agent": user_agent})
            return _response_handler(download_url, response)

        def _retrieve_codeforces_submission(view_link):
            response = requests.get(view_link)
            return _response_handler(view_link, response)

        for site in sites_with_download_functionality:
            method_name = locals()["_retrieve_%s_submission" % site.lower()]
            if method_name(assertion_hash[site]["view_link"]) != assertion_hash[site]["submission"]:
                raise RuntimeError(site + " download submission failed")

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
                    "test_download_submission"]:
    res = test_retrieval(rt, method_name)
    if res != "Success":
        pushover_message += res + "\n"

if pushover_message != "":
    response = requests.post("https://api.pushover.net/1/messages.json",
                             data={"token": current.pushover_api_token,
                                   "user": current.pushover_user_token,
                                   "message": pushover_message.strip(),
                                   "title": "Extras retrieval failure",
                                   "priority": 1}).json()

