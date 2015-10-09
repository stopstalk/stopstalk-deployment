"""
    Run the script on the risk of losing all the submissions
    of all the users and Custom users

    Usage:
    ------
    Go to the web2py directory
    Execute:
        `python web2py.py -S stopstalk -M -R applications/stopstalk/static/scripts/resetDB.py`
    Restart the web2py server
    Open the Index page again
"""
db.submission.truncate()
print "Successfully deleted all submissions"

auth_user_update = db(db.auth_user.id > 0).update(last_retrieved="2013-01-01 00:00:00",
                                                  per_day=0.0)
if auth_user_update:
    print "Update on auth_user completed"
else:
    print "auth_user was not updated"

custom_friend_update = db(db.custom_friend.id > 0).update(last_retrieved="2013-01-01 00:00:00",
                                                          per_day=0.0)
if custom_friend_update:
    print "Update on custom_friend completed"
else:
    print "custom_friend was not updated"

db.commit()
