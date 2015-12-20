# -*- coding: utf-8 -*-
"""
    Copyright (c) 2015 Raj Patel(raj454raj@gmail.com), StopStalk

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

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
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

extra_fields = [Field("institute", requires=IS_NOT_EMPTY()),
                Field("stopstalk_handle",
                      requires=[IS_NOT_IN_DB(db,
                                             "auth_user.stopstalk_handle",
                                             error_message=T("Handle taken")),
                                             IS_NOT_IN_DB(db,
                                                          "custom_friend.stopstalk_handle",
                                                          error_message=T("Handle taken"))]
                                             ),
                Field("rating",
                      default=0,
                      writable=False),
                Field("last_retrieved", "datetime",
                      default=initial_date,
                      writable=False),
                Field("per_day", "double",
                      default=0.0,
                      writable=False),
                Field("referrer",
                      label="Referrer's StopStalk Handle",
                      default=""),
                ]

site_handles = []
for site in current.SITES:
    site_handles += [Field(site.lower() + "_handle")]

extra_fields += site_handles
auth.settings.extra_fields["auth_user"] = extra_fields

auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = current.smtp_server
mail.settings.sender = current.sender_mail
mail.settings.login = current.sender_mail + ":" + current.sender_password

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True
auth.settings.formstyle = materialize_form

auth.messages.email_sent = 'Verification Email sent'
auth.messages.logged_out = 'Successfully logged out'
auth.messages.invalid_login = 'Invalid login credentials'
current.response.formstyle = materialize_form

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

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

custom_friend_fields = [Field("user_id", "reference auth_user"),
                        Field("first_name", requires=IS_NOT_EMPTY()),
                        Field("last_name", requires=IS_NOT_EMPTY()),
                        Field("institute", requires=IS_NOT_EMPTY()),
                        Field("stopstalk_handle", requires = [IS_NOT_IN_DB(db,
                                                                           "auth_user.stopstalk_handle",
                                                                           error_message=T("Handle already exists")),
                                                              IS_NOT_IN_DB(db,
                                                                           "custom_friend.stopstalk_handle",
                                                                           error_message=T("Handle already exists"))]),
                        Field("rating",
                              default=0,
                              writable=False),
                        Field("last_retrieved", "datetime",
                              default=initial_date,
                              writable=False),
                        Field("per_day", "double",
                              default=0.0,
                              writable=False),
                        ]

custom_friend_fields += site_handles
db.define_table("custom_friend",
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
                      default="",
                      ),
                )

db.define_table("friend_requests",
                Field("from_h", "reference auth_user"),
                Field("to_h", "reference auth_user"),
                )

db.define_table("friends",
                Field("user_id", "reference auth_user"),
                Field("friend_id", "reference auth_user"))

db.define_table("problem_tags",
                Field("problem_link"),
                Field("tags",
                      default="-"))

db.define_table("contact_us",
                Field("name", requires=IS_NOT_EMPTY()),
                Field("phone_number", requires=IS_NOT_EMPTY()),
                Field("email", requires=[IS_NOT_EMPTY(), IS_EMAIL()]),
                Field("subject", requires=IS_NOT_EMPTY()),
                # @ToDo: Not working for some reason
                Field("text_message", "text", requires=IS_NOT_EMPTY()))

current.db = db
