# -*- coding: utf-8 -*-
"""
    Copyright (c) 2015-2016 Raj Patel(raj454raj@gmail.com), StopStalk

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

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Mail

## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('mysql://' + current.mysql_user + \
             ':' + current.mysql_password + \
             '@' + current.mysql_server + \
             '/' + current.mysql_dbname)
#    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*']
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager
from datetime import datetime
from utilities import materialize_form

auth = Auth(db)
service = Service()
plugins = PluginManager()

initial_date = datetime.strptime("2013-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

db.define_table("institutes",
                Field("name"))

itable = db.institutes
all_institutes = db(itable).select(itable.name,
                                   orderby=itable.name)
all_institutes = [x["name"].strip("\"") for x in all_institutes]
all_institutes.append("Other")
extra_fields = [Field("institute",
                      requires=IS_IN_SET(all_institutes,
                                         zero="Institute",
                                         error_message="Institute Required")),
                Field("stopstalk_handle",
                      requires=[IS_NOT_IN_DB(db,
                                             "auth_user.stopstalk_handle",
                                             error_message=T("Handle taken")),
                                IS_NOT_IN_DB(db,
                                             "custom_friend.stopstalk_handle",
                                             error_message=T("Handle taken"))]),
                Field("rating",
                      default=0,
                      writable=False),
                Field("prev_rating",
                      default=0,
                      writable=False),
                Field("per_day", "double",
                      default=0.0,
                      writable=False),
                Field("per_day_change",
                      default="0.0",
                      writable=False),
                Field("referrer",
                      label="Referrer's StopStalk Handle",
                      default=""),
                Field("allowed_cu", "integer",
                      default=3,
                      readable=False,
                      writable=False),
                Field("blacklisted", "boolean",
                      default=False,
                      readable=False,
                      writable=False),
                Field("authentic", "boolean",
                      default=False,
                      readable=False,
                      writable=False)]

site_handles = []
all_last_retrieved = []
for site in current.SITES:
    site_handles.append(Field(site.lower() + "_handle"))
    all_last_retrieved.append(Field(site.lower() + "_lr", "datetime",
                                    default=initial_date,
                                    writable=False))

extra_fields += site_handles
extra_fields += all_last_retrieved
auth.settings.extra_fields["auth_user"] = extra_fields

auth.define_tables(username=False, signature=False)

## configure email

# Normal mails go through contactstopstalk@gmail.com
mail = auth.settings.mailer
mail.settings.server = current.smtp_server
mail.settings.sender = "Team StopStalk <" + current.sender_mail + ">"
mail.settings.login = current.sender_mail + ":" + current.sender_password

# Bulk emails go through admin@stopstalk.com
bulkmail = Mail()
bulkmail.settings.server = current.bulk_smtp_server
bulkmail.settings.sender = "Team StopStalk <" + current.bulk_sender_mail + ">"
bulkmail.settings.login = current.bulk_sender_mail + ":" + current.bulk_sender_password

# -----------------------------------------------------------------------------
def send_mail(to, subject, message, mail_type, bulk=False):
    """
        Email sending helper wrapper around Web2Py Mailer

        @param to (String): Recipient of the mail
        @param subject (String): Subject of the mail
        @param message (String): Message body of the mail
        @param mail_type (String): Mail type (used for handling subscriptions)
        @param bulk (Boolean): Bulk sending mail
    """

    # Check if user has unsubscribed from email updates
    utable = db.unsubscriber

    query = (utable.email == to)
    if mail_type != "admin":
        query &= (utable[mail_type] == False)

    row = db(query).select().first()

    if row is None:
        if bulk:
            db.queue.insert(status="pending",
                            email=to,
                            subject=subject,
                            message=message)
        else:
            mail.send(to=to,
                      subject=subject,
                      message=message)

current.send_mail = send_mail
## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.reset_password_requires_verification = True
auth.settings.formstyle = materialize_form
auth.settings.login_next = URL("default", "index")

auth.messages.email_sent = "Verification Email sent"
auth.messages.logged_out = "Successfully logged out"
auth.messages.invalid_login = "Invalid login credentials"
auth.messages.label_remember_me = "Remember credentials"
auth.settings.long_expiration = 3600 * 24 * 366 # Remember me for a year

# -----------------------------------------------------------------------------
def validate_email(email):
    """
        Check if an email is from a valid domain name

        @param email (String): Email address
        @return (Boolean): Valid email or not
    """

    if email.strip() == "":
        return False

    domain = email.split("@")[-1]
    # Temporary fix
    if domain == "yahoo.com":
        return True

    import requests

    try:
        response = requests.get("http://" + domain, timeout=5)
        return (response.status_code == 200)
    except:
        return False

# -----------------------------------------------------------------------------
def sanitize_fields(form):
    """
        Display errors for the following:

        1. Strip whitespaces from all the fields
        2. Remove @ from the HackerEarth
        3. Lowercase the handles
        4. Fill the institute field with "Other" if empty
        5. Email address entered is from a valid domain
        6. Email address instead of handles
        7. Spoj follows a specific convention for handle naming
        8. stopstalk_handle is alphanumeric

        @param form (FORM): Registration / Add Custom friend form
    """

    from re import match

    # 8.
    stopstalk_handle_error = "Expected alphanumeric (Underscore allowed)"
    try:
        group = match("[0-9a-zA-Z_]*", form.vars.stopstalk_handle).group()
        if group != form.vars.stopstalk_handle:
            form.errors.stopstalk_handle = stopstalk_handle_error
    except AttributeError:
        form.errors.stopstalk_handle = stopstalk_handle_error

    def _remove_at_symbol(site_name):
        if site_name in current.SITES:
            field = site_name.lower() + "_handle"
            if form.vars[field] and form.vars[field][0] == "@":
                form.errors[field] = "@ symbol not required"

    def _valid_spoj_handle(handle):
        try:
            return match("[a-z]+[0-9a-z_]*", handle).group() == handle
        except AttributeError:
            return False

    handle_fields = ["stopstalk"]
    handle_fields.extend([x.lower() for x in current.SITES.keys()])

    # 1. and 6.
    for field in handle_fields:
        field_handle = field + "_handle"
        if form.vars[field_handle].__contains__(" "):
            form.errors[field_handle] = "White spaces not allowed"
        if IS_EMAIL(error_message="check")(form.vars[field_handle])[1] != "check":
            form.errors[field_handle] = "Email address instead of handle"

    # 2.
    _remove_at_symbol("HackerEarth")

    # 7.
    if "Spoj" in current.SITES:
        if form.vars["spoj_handle"] and \
           not _valid_spoj_handle(form.vars["spoj_handle"]):
            form.errors["spoj_handle"] = "Handle should only contain lower case letters 'a'-'z', underscores '_', digits '0'-'9', and must start with a letter!"

    # 3.
    for site in handle_fields:
        site_handle = site + "_handle"
        if form.vars[site_handle] != form.vars[site_handle].lower():
            form.errors[site_handle] = "Please enter in lower case"

    # 4.
    if form.vars.institute == "":
        form.errors.institute = "Please select an institute or Other"

    # 5.
    if form.vars.email:
        if validate_email(form.vars.email) is False:
            form.errors.email = "Invalid email address"

    if form.errors:
        response.flash = "Form has errors!!"

#-----------------------------------------------------------------------------
def notify_institute_users(record):
    """
        Send mail to all users from the same institute
        when a user registers from that institute (after email verification)

        @param record (Row): Record having the user details
    """

    atable = db.auth_user
    query = (atable.institute == record.institute) & \
            (atable.email != record.email) & \
            (atable.institute != "Other") & \
            (atable.blacklisted == False)
    rows = db(query).select(atable.email, atable.stopstalk_handle)

    subject = "New user registered from your Institute"
    for row in rows:
        message = """<html>
Hello %s,<br />

%s from your Institute has just joined StopStalk.<br />
Send a friend request now %s for better experience on StopStalk<br />

To stop receiving mails - <a href="%s">Unsubscribe</a> <br />

Regards,<br />
StopStalk
                  </html>""" % (row.stopstalk_handle,
                         record.first_name + " " + record.last_name,
                         URL("user",
                             "profile",
                             args=record.stopstalk_handle,
                             scheme=True,
                             host=True,
                             extension=False),
                         URL("default",
                             "unsubscribe",
                             scheme=True,
                             host=True,
                             extension=False))

        send_mail(to=row.email,
                  subject=subject,
                  message=message,
                  mail_type="institute_user",
                  bulk=True)

# -----------------------------------------------------------------------------
def register_callback(form):
    """
        Send mail to raj454raj@gmail.com about all the users who register

        @param form (FORM): Register form
    """

    # Send mail to raj454raj@gmail.com
    to = "raj454raj@gmail.com"
    subject = "New user registered"
    message = """
Name: %s %s
Email: %s
Institute: %s
StopStalk handle: %s
Referrer: %s
Codechef handle: %s
Codeforces handle: %s
Spoj handle: %s
HackerEarth handle: %s
HackerRank handle: %s
              """ % (form.vars.first_name,
                     form.vars.last_name,
                     form.vars.email,
                     form.vars.institute,
                     form.vars.stopstalk_handle,
                     form.vars.referrer,
                     form.vars.codechef_handle,
                     form.vars.codeforces_handle,
                     form.vars.spoj_handle,
                     form.vars.hackerearth_handle,
                     form.vars.hackerrank_handle)
    send_mail(to=to, subject=subject, message=message, mail_type="admin")

auth.settings.register_onvalidation = [sanitize_fields]
auth.settings.register_onaccept.append(register_callback)
auth.settings.verify_email_onaccept.append(notify_institute_users)
current.auth = auth
current.response.formstyle = materialize_form
current.sanitize_fields = sanitize_fields

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

custom_friend_fields = [Field("user_id", "reference auth_user"),
                        Field("first_name", requires=IS_NOT_EMPTY()),
                        Field("last_name", requires=IS_NOT_EMPTY()),
                        Field("institute",
                              requires=IS_IN_SET(all_institutes,
                                                 zero="Institute")),
                        Field("stopstalk_handle", requires = [IS_NOT_IN_DB(db,
                                                                           "auth_user.stopstalk_handle",
                                                                           error_message=T("Handle already exists")),
                                                              IS_NOT_IN_DB(db,
                                                                           "custom_friend.stopstalk_handle",
                                                                           error_message=T("Handle already exists"))]),
                        Field("rating",
                              default=0,
                              writable=False),
                        Field("prev_rating",
                              default=0,
                              writable=False),
                        Field("per_day", "double",
                              default=0.0,
                              writable=False),
                        Field("per_day_change",
                              default="0.0",
                              writable=False),
                        Field("duplicate_cu", "reference custom_friend",
                              default=None)]

custom_friend_fields += site_handles
custom_friend_fields += all_last_retrieved
db.define_table("custom_friend",
                format="%(first_name)s %(last_name)s (%(id)s)",
                *custom_friend_fields)

db.define_table("submission",
                Field("user_id", "reference auth_user"),
                Field("custom_user_id", "reference custom_friend"),
                Field("stopstalk_handle"),
                Field("site_handle"),
                Field("site"),
                Field("time_stamp", "datetime"),
                Field("problem_name"),
                Field("problem_link"),
                Field("lang"),
                Field("status"),
                Field("points"),
                Field("view_link",
                      default=""))

db.define_table("friend_requests",
                Field("from_h", "reference auth_user"),
                Field("to_h", "reference auth_user"),
                )

db.define_table("friends",
                Field("user_id", "reference auth_user"),
                Field("friend_id", "reference auth_user"))

db.define_table("problem_tags",
                Field("problem_link"),
                Field("problem_name"),
                Field("tags",
                      default="['-']"),
                Field("problem_added_on", "date"))

db.define_table("problem_editorial",
                Field("problem_link"),
                Field("editorial_link", default=None),
                Field("problem_added_on", "date"))

db.define_table("problem",
                Field("name"),
                Field("link"),
                Field("tags", default="['-']"),
                Field("editorial_link", default=None),
                Field("tags_added_on", "date"),
                Field("editorial_added_on", "date"))

db.define_table("contact_us",
                Field("name", requires=IS_NOT_EMPTY()),
                Field("email", requires=[IS_NOT_EMPTY(), IS_EMAIL()]),
                Field("phone_number", requires=IS_NOT_EMPTY()),
                Field("subject", requires=IS_NOT_EMPTY()),
                # @ToDo: Not working for some reason
                Field("text_message", "text", requires=IS_NOT_EMPTY()))

db.define_table("faq",
                Field("question", requires=IS_NOT_EMPTY()),
                Field("answer", requires=IS_NOT_EMPTY()))

db.define_table("stickers_given",
                Field("user_id", "reference auth_user"),
                Field("sticker_count", "integer"))

db.define_table("unsubscriber",
                Field("email",
                      requires=IS_EMAIL()),
                Field("friend_requests",
                      "boolean",
                      default=True,
                      label="Friend requests from users"),
                Field("acceptance_rejectance",
                      "boolean",
                      default=True,
                      label="Acceptance/Rejectance of friend requests"),
                Field("unfriend",
                      "boolean",
                      default=True,
                      label="Notify when a friend unfriends me on StopStalk"),
                Field("feature_updates",
                      "boolean",
                      default=True,
                      label="New feature updates from StopStalk"),
                Field("pending_requests",
                      "boolean",
                      default=True,
                      label="Weekly reminder for pending friend requests"),
                Field("institute_user",
                      "boolean",
                      default=True,
                      label="Notify when a user from your Institute registers"))

site_fields = []
for site in current.SITES:
    site_fields.append(Field(site.lower(), "integer", default=0))

db.define_table("queue",
                Field("status"),
                Field("email"),
                Field("subject"),
                Field("message", "text"))

db.define_table("sessions_today",
                Field("message", "string"))

db.define_table("download_submission_logs",
                Field("user_id", "reference auth_user"),
                Field("url", "string"))

db.define_table("failed_retrieval",
                Field("user_id", "reference auth_user"),
                Field("custom_user_id", "reference custom_friend"))

db.define_table("invalid_handle",
                Field("handle"),
                Field("site"))

db.define_table("contest_logging",
                Field("click_type"),
                Field("contest_details", "text"),
                Field("stopstalk_handle"),
                Field("time_stamp", "datetime"))

def get_solved_problems(user_id):
    """
        Get the solved and unsolved problems of a user

        @param user_id(Integer): user_id of the logged in user
    """
    try:
        # Session variables already set
        current.solved_problems
        current.unsolved_problems
        return
    except AttributeError:
        pass

    stable = db.submission
    query = (stable.user_id == user_id) & (stable.status == "AC")
    problems = db(query).select(stable.problem_link, distinct=True)
    solved_problems = set([x.problem_link for x in problems])

    query = (stable.user_id == user_id)
    problems = db(query).select(stable.problem_link, distinct=True)
    all_problems = set([x.problem_link for x in problems])
    unsolved_problems = all_problems - solved_problems

    current.solved_problems = solved_problems
    current.unsolved_problems = unsolved_problems

if session["auth"]:
    session["handle"] = session["auth"]["user"]["stopstalk_handle"]
    session["user_id"] = session["auth"]["user"]["id"]
    get_solved_problems(session["user_id"])
else:
    current.solved_problems = set([])
    current.unsolved_problems = set([])

current.db = db

# =============================================================================
