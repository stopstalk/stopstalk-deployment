PROXY = {"http": "http://proxy.iiit.ac.in:8080/",
         "https": "http://proxy.iiit.ac.in:8080/"}
user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"

import requests
import gevent
from gevent import queue, monkey
from gevent.pool import Group

monkey.patch_all(thread=False)

count = 1

def fetch(pid):
    global count
    while True:
        tmp = requests.get("https://www.codechef.com/recent/user?user_handle=tryingtocode&page=4",
                           headers={"User-Agent": user_agent},
                           proxies=PROXY)
        count += 1
        if tmp.status_code == 200:
            break
    print tmp

def synchronous():
    for i in range(1,100):
        fetch(i)

def asynchronous():
    threads = []
    for i in xrange(100):
        threads.append(gevent.spawn(fetch, i))
    gevent.joinall(threads)

print('Synchronous:')
synchronous()

print('Asynchronous:')
asynchronous()
print count
