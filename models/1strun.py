from gluon import *
# Configure mysql server
current.mysql_user = "root"
current.mysql_password = "##########"
current.mysql_server = "localhost"
current.mysql_dbname = "migration"

# Configure mail options
current.smtp_server = "smtp.gmail.com:587"
current.sender_mail = "contactstopstalk@gmail.com"
current.sender_password = ""
current.SITES = {"CodeChef": "http://www.codechef.com/users/",
                 "CodeForces": "http://www.codeforces.com/profile/",
                 "Spoj": "http://www.spoj.com/users/",
                 "HackerEarth": "https://hackerearth.com/users/"}
