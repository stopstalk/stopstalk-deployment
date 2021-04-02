set -e
/usr/bin/mysqldump -u root stopstalkdb > /root/stopstalk-logs/stopstalkdb.sql
sleep 10
/usr/bin/mysqldump -u root uvajudge > /root/stopstalk-logs/uvajudge.sql
sleep 10

/usr/local/bin/aws s3 cp /root/stopstalk-logs/ s3://stopstalk-db-dumps/mysql/ --recursive --exclude "*" --include "*.sql"
