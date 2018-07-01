import bs4, requests, time, datetime, pprint

pp = pprint.PrettyPrinter(indent=2)

timus_id = "19306"
acm_link = "http://acm.timus.ru/"
submissions = []
from_id = None
count = 1000
for i in xrange(1000):
    initial_url = acm_link + "status.aspx?author=" + timus_id + "&count=" + str(count)
    if from_id is None:
        url = initial_url
    else:
        url = initial_url + "&from=" + str(from_id)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    table = soup.find("table", class_="status")
    all_trs = table.find_all("tr")
    print "****************"
    print map(lambda x: x.text, all_trs[:2])
    print "****************"
    print map(lambda x: x.text, all_trs[-2:])
    print "****************"
    trs = all_trs[2:-2]

    for tr in trs:
        tds = tr.find_all("td")
        from_id = int(tds[0].text)
        curr, _, date = tds[1].contents
        curr = time.strptime(curr.text + " " + date.text, "%H:%M:%S %d %b %Y")
        curr = time.strptime(str(datetime.datetime(curr.tm_year,
                                                   curr.tm_mon,
                                                   curr.tm_mday,
                                                   curr.tm_hour,
                                                   curr.tm_min,
                                                   curr.tm_sec) + \
                                                   datetime.timedelta(minutes=30)),
                             "%Y-%m-%d %H:%M:%S")


        problem_link = acm_link + tds[3].contents[0]["href"]
        problem_name = tds[3].text
        language = tds[4].text
        status = tds[5].text
        submission_status = None
        if status == "Accepted":
            submission_status = "AC"
        elif status == "Wrong answer":
            submission_status = "WA"
        elif status.__contains__("Runtime error"):
            submission_status = "RE"
        elif status == "Memory limit exceeded":
            submission_status = "MLE"
        elif status == "Time limit exceeded":
            submission_status = "TLE"
        elif status == "Compilation error":
            submission_status = "CE"
        else:
            submission_status = "OTH"

        if submission_status == "AC":
            points = "100"
        else:
            points = "0"

        submissions.append((str(time.strftime("%Y-%m-%d %H:%M:%S", curr)),
                            problem_link,
                            problem_name,
                            submission_status,
                            points,
                            language,
                            ""))
        from_id -= 1

    if len(trs) < count:
        break
print len(submissions)
#pp.pprint(submissions)