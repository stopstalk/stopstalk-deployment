# -*- coding: utf-8 -*-
"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

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

import json as json_for_views
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    mysql_connection = 'mysql://' + current.mysql_user + \
                       ':' + current.mysql_password + \
                       '@' + current.mysql_server

    db = DAL(mysql_connection + '/' + current.mysql_dbname,
             table_hash="stopstalkdb")
    uvadb = DAL(mysql_connection + '/' + current.mysql_uvadbname,
                table_hash="uvajudge")

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

from gluon.tools import Auth, Service, PluginManager, AuthJWT
import datetime
import utilities
from stopstalk_constants import *

auth = Auth(db)
auth_jwt = AuthJWT(auth, secret_key=current.jwt_secret, user_param="email")
service = Service()
plugins = PluginManager()

all_countries = {'Canada': 'CA', 'Moldova (Republic of)': 'MD', 'Sao Tome and Principe': 'ST', 'Guinea-Bissau': 'GW', 'United States of America': 'US', 'Lithuania': 'LT', 'Cambodia': 'KH', 'Saint Helena, Ascension and Tristan da Cunha': 'SH', 'Switzerland': 'CH', 'Ethiopia': 'ET', 'Aruba': 'AW', 'Saint Martin (French part)': 'MF', 'Solomon Islands': 'SB', 'Argentina': 'AR', 'Cameroon': 'CM', 'Burkina Faso': 'BF', 'Turkmenistan': 'TM', 'Ghana': 'GH', 'Saudi Arabia': 'SA', 'Rwanda': 'RW', 'Togo': 'TG', 'Japan': 'JP', 'American Samoa': 'AS', 'United States Minor Outlying Islands': 'UM', 'Cocos (Keeling) Islands': 'CC', 'Pitcairn': 'PN', 'Guatemala': 'GT', 'Bosnia and Herzegovina': 'BA', 'Kuwait': 'KW', 'Russian Federation': 'RU', 'Jordan': 'JO', 'Bonaire, Sint Eustatius and Saba': 'BQ', 'Dominica': 'DM', 'Liberia': 'LR', 'Maldives': 'MV', 'Jamaica': 'JM', 'Oman': 'OM', 'Martinique': 'MQ', 'Cabo Verde': 'CV', 'Christmas Island': 'CX', 'French Guiana': 'GF', 'Niue': 'NU', 'Monaco': 'MC', 'Wallis and Futuna': 'WF', 'New Zealand': 'NZ', 'Yemen': 'YE', 'Jersey': 'JE', 'Andorra': 'AD', 'Albania': 'AL', 'Samoa': 'WS', 'Norfolk Island': 'NF', 'United Arab Emirates': 'AE', 'Guam': 'GU', 'India': 'IN', 'Azerbaijan': 'AZ', 'Lesotho': 'LS', 'Saint Vincent and the Grenadines': 'VC', 'Kenya': 'KE', 'Macao': 'MO', 'Turkey': 'TR', 'Afghanistan': 'AF', 'Virgin Islands (British)': 'VG', 'Bangladesh': 'BD', 'Mauritania': 'MR', 'Congo (Democratic Republic of the)': 'CD', 'Turks and Caicos Islands': 'TC', 'Saint Lucia': 'LC', 'San Marino': 'SM', 'French Polynesia': 'PF', 'France': 'FR', 'Svalbard and Jan Mayen': 'SJ', 'Syrian Arab Republic': 'SY', 'Bermuda': 'BM', 'Slovakia': 'SK', 'Somalia': 'SO', 'Peru': 'PE', 'Swaziland': 'SZ', 'Nauru': 'NR', 'Seychelles': 'SC', 'Norway': 'NO', 'Malawi': 'MW', 'Cook Islands': 'CK', 'Benin': 'BJ', 'Western Sahara': 'EH', 'Cuba': 'CU', 'Montenegro': 'ME', 'Falkland Islands (Malvinas)': 'FK', 'Mayotte': 'YT', 'Heard Island and McDonald Islands': 'HM', 'China': 'CN', 'Armenia': 'AM', 'Timor-Leste': 'TL', 'Dominican Republic': 'DO', 'Bolivia (Plurinational State of)': 'BO', 'Ukraine': 'UA', 'Bahrain': 'BH', 'Tonga': 'TO', 'Finland': 'FI', 'Libya': 'LY', 'Macedonia (the former Yugoslav Republic of)': 'MK', 'Cayman Islands': 'KY', 'Central African Republic': 'CF', 'New Caledonia': 'NC', 'Mauritius': 'MU', 'Tajikistan': 'TJ', 'Liechtenstein': 'LI', 'Australia': 'AU', 'Mali': 'ML', 'Sweden': 'SE', 'Bulgaria': 'BG', 'Palestine, State of': 'PS', "Korea (Democratic People's Republic of)": 'KP', 'Romania': 'RO', 'Angola': 'AO', 'French Southern Territories': 'TF', 'Chad': 'TD', 'South Africa': 'ZA', 'Tokelau': 'TK', 'Cyprus': 'CY', 'South Georgia and the South Sandwich Islands': 'GS', 'Brunei Darussalam': 'BN', 'Qatar': 'QA', 'Malaysia': 'MY', 'Austria': 'AT', 'Mozambique': 'MZ', 'Uganda': 'UG', 'Hungary': 'HU', 'Niger': 'NE', 'Isle of Man': 'IM', 'Brazil': 'BR', 'Virgin Islands (U.S.)': 'VI', 'Faroe Islands': 'FO', 'Guinea': 'GN', 'Panama': 'PA', 'Guyana': 'GY', 'Costa Rica': 'CR', 'Luxembourg': 'LU', 'Bahamas': 'BS', 'Gibraltar': 'GI', 'Ireland': 'IE', 'Pakistan': 'PK', 'Palau': 'PW', 'Nigeria': 'NG', 'Ecuador': 'EC', 'Czech Republic': 'CZ', 'Viet Nam': 'VN', 'Belarus': 'BY', 'Vanuatu': 'VU', 'Algeria': 'DZ', 'Slovenia': 'SI', 'El Salvador': 'SV', 'Tuvalu': 'TV', 'Saint Pierre and Miquelon': 'PM', 'Iran (Islamic Republic of)': 'IR', 'Marshall Islands': 'MH', 'Chile': 'CL', 'Puerto Rico': 'PR', 'Belgium': 'BE', 'Kiribati': 'KI', 'Haiti': 'HT', 'Belize': 'BZ', 'Hong Kong': 'HK', 'Sierra Leone': 'SL', 'Georgia': 'GE', "Lao People's Democratic Republic": 'LA', 'Gambia': 'GM', 'Philippines': 'PH', 'Morocco': 'MA', 'Croatia': 'HR', 'Mongolia': 'MN', 'Guernsey': 'GG', 'Thailand': 'TH', 'Namibia': 'NA', 'Grenada': 'GD', 'Taiwan, Province of China': 'TW', 'Aland Islands': 'AX', 'Venezuela (Bolivarian Republic of)': 'VE', 'Iraq': 'IQ', 'Tanzania, United Republic of': 'TZ', 'Portugal': 'PT', 'Estonia': 'EE', 'Uruguay': 'UY', 'Equatorial Guinea': 'GQ', 'Lebanon': 'LB', 'Korea (Republic of)': 'KR', 'Uzbekistan': 'UZ', 'Tunisia': 'TN', 'Djibouti': 'DJ', 'Greenland': 'GL', 'Antigua and Barbuda': 'AG', 'Spain': 'ES', 'Colombia': 'CO', 'Burundi': 'BI', 'Fiji': 'FJ', 'Barbados': 'BB', 'Madagascar': 'MG', 'Italy': 'IT', 'Bhutan': 'BT', 'Sudan': 'SD', 'Nepal': 'NP', 'Malta': 'MT', 'Netherlands': 'NL', 'Northern Mariana Islands': 'MP', 'Suriname': 'SR', 'United Kingdom of Great Britain and Northern Ireland': 'GB', 'Anguilla': 'AI', 'Republic of Kosovo': 'XK', 'Micronesia (Federated States of)': 'FM', 'Holy See': 'VA', 'Israel': 'IL', 'Reunion': 'RE', 'Indonesia': 'ID', 'Iceland': 'IS', 'Zambia': 'ZM', 'Senegal': 'SN', 'Papua New Guinea': 'PG', 'Saint Kitts and Nevis': 'KN', 'Trinidad and Tobago': 'TT', 'Zimbabwe': 'ZW', 'Germany': 'DE', 'Denmark': 'DK', 'Kazakhstan': 'KZ', 'Poland': 'PL', 'Eritrea': 'ER', 'Kyrgyzstan': 'KG', 'Saint Barthelemy': 'BL', 'British Indian Ocean Territory': 'IO', 'Montserrat': 'MS', 'Mexico': 'MX', 'Sri Lanka': 'LK', 'Latvia': 'LV', 'South Sudan': 'SS', 'Curacao': 'CW', 'Guadeloupe': 'GP', "Cote d'Ivoire": 'CI', 'Honduras': 'HN', 'Myanmar': 'MM', 'Bouvet Island': 'BV', 'Egypt': 'EG', 'Nicaragua': 'NI', 'Singapore': 'SG', 'Serbia': 'RS', 'Botswana': 'BW', 'Antarctica': 'AQ', 'Congo': 'CG', 'Sint Maarten (Dutch part)': 'SX', 'Greece': 'GR', 'Paraguay': 'PY', 'Gabon': 'GA', 'Comoros': 'KM'}
reverse_country_mapping = dict([(x[1], x[0]) for x in list(all_countries.items())])
current.all_countries = all_countries
country_name_list = list(all_countries.keys())
country_name_list.sort()

# To disable writing of translations
# http://www.web2py.com/books/default/chapter/29/04#Translating-variables
T.is_writable = False

initial_date = datetime.datetime.strptime(current.INITIAL_DATE, "%Y-%m-%d %H:%M:%S")

db.define_table("institutes",
                Field("name", label=T("Name")))

itable = db.institutes
all_institutes = db(itable).select(itable.name,
                                   orderby=itable.name)
all_institutes = [x["name"].strip("\"") for x in all_institutes]
all_institutes.append("Other")
extra_fields = [Field("institute",
                      label=T("Institute"),
                      requires=IS_IN_SET(all_institutes,
                                         zero=T("Institute"),
                                         error_message=T("Institute required")),
                      comment=T("Write to us if your Institute is not listed")),
                Field("country",
                      label=T("Country"),
                      requires=IS_IN_SET(country_name_list,
                                         zero=T("country"),
                                         error_message=T("Country required")),
                      comment=T("Write to us if your Country is not listed"),
                      default=""),
                Field("stopstalk_handle",
                      label=T("StopStalk handle"),
                      requires=[IS_NOT_EMPTY(error_message=auth.messages.is_empty),
                                IS_NOT_IN_DB(db,
                                             "auth_user.stopstalk_handle",
                                             error_message=T("Handle taken")),
                                IS_NOT_IN_DB(db,
                                             "custom_friend.stopstalk_handle",
                                             error_message=T("Handle taken"))],
                      comment=T("Unique handle to identify distinctly on StopStalk")),
                Field("rating",
                      default=0,
                      writable=False),
                Field("prev_rating",
                      default=0,
                      writable=False),
                Field("stopstalk_rating", "integer",
                      default=0,
                      writable=False),
                Field("stopstalk_prev_rating", "integer",
                      default=0,
                      writable=False),
                Field("per_day", "double",
                      default=0.0,
                      writable=False),
                Field("per_day_change",
                      default="0.0",
                      writable=False),
                Field("referrer",
                      label=T("Referrer's StopStalk Handle"),
                      default="",
                      comment=T("StopStalk handle of a verified user")),
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
                      writable=False),
                Field("graph_data_retrieved", "boolean",
                      default=False,
                      readable=False,
                      writable=False),
                Field("refreshed_timestamp",
                      "datetime",
                      default=initial_date,
                      writable=False)]

site_handles = []
all_last_retrieved = []
for site in current.SITES:
    site_handles.append(Field(site.lower() + "_handle",
                              label=site + " handle"))
    all_last_retrieved.append(Field(site.lower() + "_lr", "datetime",
                                    default=initial_date,
                                    writable=False))

extra_fields += site_handles
extra_fields += all_last_retrieved
auth.settings.extra_fields["auth_user"] = extra_fields
auth.settings.logging_enabled = False

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
bulkmail.settings.login = current.bulk_sender_user + ":" + current.bulk_sender_password

from redis import Redis
from influxdb import InfluxDBClient

# REDIS CLIENT
current.REDIS_CLIENT = Redis(host=current.redis_server, port=current.redis_port, db=0)

# INFLUX CLIENT
current.INFLUXDB_CLIENT = InfluxDBClient(current.influxdb_server,
                                         current.influxdb_port,
                                         current.influxdb_user,
                                         current.influxdb_password,
                                         INFLUX_DBNAME)


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

    if row is None or mail_type == "admin":
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
auth.settings.formstyle = utilities.materialize_form
auth.settings.login_next = URL("default", "index")

auth.messages.email_sent = T("Verification Email sent")
auth.messages.logged_out = T("Successfully logged out")
auth.messages.invalid_login = T("Invalid login credentials")
auth.messages.label_remember_me = T("Remember credentials")
auth.settings.long_expiration = 3600 * 24 * 60 # Remember me for two months

# -----------------------------------------------------------------------------
def validate_email(email):
    """
        Check if an email is from a valid domain name

        @param email (String): Email address
        @return (Boolean): Valid email or not
    """

    if email.strip() == "":
        return False

    if email.__contains__("@iiita.ac.in"):
        return True

    import requests

    def _fallback_email_validation(email):
        """
            Called in the following cases

            1. access_key is empty or not mentioned in 0firstrun.py
            2. Network failure for NeverBounce API
        """
        domain = email.split("@")[-1]
        try:
            response = requests.get("http://" + domain,
                                    headers={"User-Agent": COMMON_USER_AGENT},
                                    timeout=3)
            return (response.status_code == 200)
        except:
            return False

    attable = db.access_tokens
    query = (attable.time_stamp > (datetime.datetime.now() - \
                                   datetime.timedelta(minutes=55))) & \
            (attable.type == "NeverBounce access_token")
    row = db(query).select(orderby="<random>").first()
    if row:
        access_token = row.value
    else:
        return _fallback_email_validation(email)

    response = requests.post("https://api.neverbounce.com/v3/single",
                             data={"access_token": access_token,
                                   "email": email})
    if response.status_code == 200:
        response = response.json()
        if response["success"]:
            return (response["result"] not in (1, 4))
        else:
            return _fallback_email_validation(email)
    else:
        return _fallback_email_validation(email)

# -----------------------------------------------------------------------------
def sanitize_fields(form):
    """
        Display errors for the following:

        1.  Strip whitespaces from all the fields
        2.  Remove @ from the HackerEarth
        3.  Lowercase the handles
        4.  Fill the institute field with "Other" if empty
        5.  Email address entered is from a valid domain
        6.  Email address instead of handles
        7.  Spoj follows a specific convention for handle naming
        8.  stopstalk_handle is alphanumeric
        9.  Country field is compulsory
        10. Only positive ints allowed in Timus field
        11. HackerRank handle should not be containing hr_r=1

        @param form (FORM): Registration / Add Custom friend form
    """

    from re import match

    if form.vars.stopstalk_handle:
        # 8.
        if not utilities.is_valid_stopstalk_handle(form.vars.stopstalk_handle):
            form.errors.stopstalk_handle = T("Expected alphanumeric (Underscore allowed)")

    def _remove_at_symbol(site_name):
        if site_name in current.SITES:
            field = site_name.lower() + "_handle"
            if form.vars[field] and form.vars[field][0] == "@":
                form.errors[field] = T("@ symbol not required")

    def _valid_spoj_handle(handle):
        try:
            return match("[a-z]+[0-9a-z_]*", handle).group() == handle
        except AttributeError:
            return False

    handle_fields = ["stopstalk"]
    handle_fields.extend([x.lower() for x in list(current.SITES.keys())])

    # 1, 6 and 11
    for field in handle_fields:
        field_handle = field + "_handle"
        if form.vars[field_handle]:
            if field != "uva" and form.vars[field_handle].__contains__(" "):
                form.errors[field_handle] = T("White spaces not allowed")
            elif IS_EMAIL(error_message="check")(form.vars[field_handle])[1] != "check":
                form.errors[field_handle] = T("Email address instead of handle")
            elif field == "hackerrank" and form.vars[field_handle].__contains__("hr_r=1"):
                form.errors[field_handle] = T("Please enter only the handle")

    # 2.
    _remove_at_symbol("HackerEarth")

    # 7.
    if "Spoj" in current.SITES:
        if form.vars["spoj_handle"] and \
           not _valid_spoj_handle(form.vars["spoj_handle"]):
            form.errors["spoj_handle"] = T("Handle should only contain lower case letters 'a'-'z', underscores '_', digits '0'-'9', and must start with a letter!")

    # 3.
    for site in handle_fields:
        site_handle = site + "_handle"
        if site in ["hackerrank", "uva", "stopstalk", "atcoder"]:
            continue
        if form.vars[site_handle] and \
           form.vars[site_handle] != form.vars[site_handle].lower():
            form.vars[site_handle] = form.vars[site_handle].lower()

    # 4.
    if form.vars.institute == "":
        form.errors.institute = T("Please select an institute or Other")

    # 9.
    if form.vars.country == "":
        form.errors.country = T("Country required")

    # 5.
    if form.vars.email:
        if validate_email(form.vars.email) is False:
            form.errors.email = T("Invalid email address")

    # 10.
    if form.vars.timus_handle:
        try:
            timus_id = int(form.vars.timus_handle)
            if timus_id <= 0:
                form.errors.timus_handle = "Timus handle / ID should be a number"
        except ValueError:
            form.errors.timus_handle = "Timus handle / ID should be a number"

    if form.errors:
        response.flash = T("Form has errors")

#-----------------------------------------------------------------------------
def notify_institute_users(record):
    """
        Send mail to all users from the same institute
        when a user registers from that institute (after email verification)

        @param record (Row): Record having the user details
    """

    atable = db.auth_user
    iutable = db.institute_user
    query = (atable.institute == record.institute) & \
            (atable.email != record.email) & \
            (atable.institute != "Other") & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "")

    rows = db(query).select(atable.id)
    if len(rows):
        for row in rows:
            iutable.insert(send_to_id=row.id,
                           user_registered_id=record.id)
            db.commit()

def create_next_retrieval_record(record, custom=False):
    """
        Create a record corresponding to the new user

        @param record (Row): Record with the new user details
        @param custom (Boolean): If the user is a custom user
    """
    if custom:
        db.next_retrieval.insert(custom_user_id=record.id)
    else:
        db.next_retrieval.insert(user_id=record.id)

def append_user_to_refreshed_users(record):
    """
        Add the user in refreshed list to retrieve submissions asap

        @param record (Row): Record with the new user details
    """
    current.REDIS_CLIENT.rpush("next_retrieve_user", record.id)

# -----------------------------------------------------------------------------
def register_callback(form, register_type="normal"):
    """
        Send mail to raj454raj@gmail.com about all the users who register

        @param form (FORM): Register form
    """

    site_handles = []
    for site in current.SITES:
        site_handles.append(site)
    # Send mail to raj454raj@gmail.com
    to = "raj454raj@gmail.com"
    subject = "New user registered"
    message = """
Name: %s %s
Email: %s
Register Type: %s
Institute: %s
Country: %s
StopStalk handle: %s
Referrer: %s\n""" % (form.vars.first_name,
                     form.vars.last_name,
                     form.vars.email,
                     register_type,
                     form.vars.institute,
                     form.vars.country,
                     form.vars.stopstalk_handle,
                     form.vars.referrer)

    for site in current.SITES:
        message += "%s handle: %s\n" % (site, form.vars[site.lower() + "_handle"])
    send_mail(to=to, subject=subject, message=message, mail_type="admin")

auth.settings.register_onvalidation = [sanitize_fields]
auth.settings.register_onaccept.append(register_callback)
auth.settings.verify_email_onaccept.extend([notify_institute_users,
                                            create_next_retrieval_record,
                                            append_user_to_refreshed_users])
current.auth = auth
current.auth_jwt = auth_jwt
current.response.formstyle = utilities.materialize_form
current.sanitize_fields = sanitize_fields
current.register_callback = register_callback
current.notify_institute_users = notify_institute_users
current.create_next_retrieval_record = create_next_retrieval_record
current.append_user_to_refreshed_users = append_user_to_refreshed_users
current.create_next_retrieval_record = create_next_retrieval_record

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
                        Field("first_name",
                              label=T("First Name"),
                              requires=IS_NOT_EMPTY()),
                        Field("last_name",
                              label=T("Last Name"),
                              requires=IS_NOT_EMPTY()),
                        Field("institute",
                              label=T("Institute"),
                              requires=IS_IN_SET(all_institutes,
                                                 zero=T("Institute")),
                              comment=T("Write to us if your Institute is not listed")),
                        Field("country",
                              label=T("Country"),
                              requires=IS_IN_SET(country_name_list,
                                                 zero=T("country"),
                                                 error_message=T("Country required")),
                              comment=T("Write to us if your Country is not listed"),
                              default=""),
                        Field("stopstalk_handle",
                              label=T("StopStalk handle"),
                              requires=[IS_NOT_IN_DB(db,
                                                     "auth_user.stopstalk_handle",
                                                     error_message=T("Handle already exists")),
                                        IS_NOT_IN_DB(db,
                                                     "custom_friend.stopstalk_handle",
                                                     error_message=T("Handle already exists"))],
                              comment=T("Unique handle to identify distinctly on StopStalk")),
                        Field("rating",
                              default=0,
                              writable=False),
                        Field("prev_rating",
                              default=0,
                              writable=False),
                        Field("stopstalk_rating", "integer",
                              default=0,
                              writable=False),
                        Field("stopstalk_prev_rating", "integer",
                              default=0,
                              writable=False),
                        Field("per_day", "double",
                              default=0.0,
                              writable=False),
                        Field("per_day_change",
                              default="0.0",
                              writable=False),
                        Field("duplicate_cu", "reference custom_friend",
                              default=None),
                        Field("graph_data_retrieved", "boolean",
                              default=False,
                              readable=False,
                              writable=False),
                        Field("refreshed_timestamp",
                              "datetime",
                              default=initial_date,
                              writable=False)]

custom_friend_fields += site_handles
custom_friend_fields += all_last_retrieved
db.define_table("custom_friend",
                format="%(first_name)s %(last_name)s (%(id)s)",
                *custom_friend_fields)

def _count_users_lambda(row):
    if row.problem.user_ids in (None, ""):
        return 0
    else:
        return len(row.problem.user_ids) - \
               len(row.problem.user_ids.replace(",", "")) + 1

def _count_custom_users_lambda(row):
    if row.problem.custom_user_ids in (None, ""):
        return 0
    else:
        return len(row.problem.custom_user_ids) - \
               len(row.problem.custom_user_ids.replace(",", "")) + 1

db.define_table("problem",
                Field("name"),
                Field("link"),
                Field("tags", default="['-']"),
                Field("editorial_link", default=None),
                Field("tags_added_on", "date"),
                Field("editorial_added_on", "date"),
                Field("solved_submissions", "integer", default=0),
                Field("total_submissions", "integer", default=0),
                Field("user_ids", "text", default=""),
                Field("custom_user_ids", "text", default=""),
                Field("difficulty", "float"),
                Field.Virtual("user_count", _count_users_lambda),
                Field.Virtual("custom_user_count", _count_custom_users_lambda),
                format="%(name)s %(id)s")

db.define_table("submission",
                Field("user_id", "reference auth_user"),
                Field("custom_user_id", "reference custom_friend"),
                Field("stopstalk_handle"),
                Field("site_handle"),
                Field("site"),
                Field("time_stamp", "datetime"),
                Field("problem_id", "reference problem"),
                Field("problem_name"),
                Field("problem_link"),
                Field("lang"),
                Field("status"),
                Field("points"),
                Field("view_link",
                      default=""))

db.define_table("following",
                Field("user_id", "reference auth_user"),
                Field("follower_id", "reference auth_user"))

db.define_table("todays_requests",
                Field("user_id", "reference auth_user"),
                Field("follower_id", "reference auth_user"),
                Field("transaction_type"))

db.define_table("tag",
                Field("value"),
                format="%(value)s")

db.define_table("suggested_tags",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                Field("tag_id", "reference tag"))

db.define_table("contact_us",
                Field("name", requires=IS_NOT_EMPTY()),
                Field("email", requires=[IS_NOT_EMPTY(), IS_EMAIL()]),
                Field("phone_number", requires=IS_NOT_EMPTY()),
                Field("subject", requires=IS_NOT_EMPTY()),
                Field("text_message", "text", requires=IS_NOT_EMPTY()))

db.define_table("institute_user",
                Field("send_to_id", "reference auth_user"),
                Field("user_registered_id", "reference auth_user"))

db.define_table("faq",
                Field("question", requires=IS_NOT_EMPTY()),
                Field("answer", requires=IS_NOT_EMPTY()))

db.define_table("stickers_given",
                Field("user_id", "reference auth_user"),
                Field("sticker_count", "integer"))

db.define_table("unsubscriber",
                Field("email",
                      requires=IS_EMAIL()),
                Field("feature_updates",
                      "boolean",
                      default=True,
                      label=T("New feature updates from StopStalk")),
                Field("institute_user",
                      "boolean",
                      default=True,
                      label=T("Notify when a user from your Institute registers")),
                Field("friend_unfriend",
                      "boolean",
                      default=True,
                      label=T("Notify when a user adds/removes me as a friend")),
                Field("time_stamp", "datetime"))

nr_fields = [Field("user_id", "reference auth_user"),
             Field("custom_user_id", "reference custom_friend")]

for site in current.SITES:
    nr_fields.append(Field(site.lower() + "_delay", "integer", default=0))

db.define_table("next_retrieval", *nr_fields)

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
                Field("custom_user_id", "reference custom_friend"),
                Field("site"))

db.define_table("invalid_handle",
                Field("handle"),
                Field("site"))

db.define_table("contest_logging",
                Field("click_type"),
                Field("contest_details", "text"),
                Field("stopstalk_handle"),
                Field("time_stamp", "datetime"))

db.define_table("http_errors",
                Field("status_code", "integer"),
                Field("content", "text"),
                Field("user_id", "reference auth_user"))

db.define_table("todo_list",
                Field("user_id", "reference auth_user"),
                Field("problem_link"))

db.define_table("access_tokens",
                Field("value"),
                Field("time_stamp", "datetime"),
                Field("type"))

db.define_table("testimonials",
                Field("user_id", "reference auth_user"),
                Field("content", "text"),
                Field("stars"),
                Field("verification", default="pending"),
                Field("created_at", "datetime"))

# facebook_group - Notify about the new Facebook group
db.define_table("recent_announcements",
                Field("user_id", "reference auth_user"),
                Field("data", "text", default="{}"))

db.define_table("user_editorials",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                Field("added_on", "datetime"),
                Field("s3_key"),
                Field("votes", "text"),
                Field("verification", default="pending"))

db.define_table("resume_data",
                Field("user_id", "reference auth_user"),
                Field("resume_file_s3_path"),
                Field("will_relocate", "boolean"),
                Field("github_profile"),
                Field("linkedin_profile"),
                Field("join_from", "datetime"),
                Field("graduation_year"),
                Field("experience"),
                Field("fulltime_or_internship"),
                Field("contact_number"),
                Field("can_contact", "boolean"),
                Field("expected_salary"))

db.define_table("problem_difficulty",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                Field("score", "integer", default=0))

db.define_table("problem_setters",
                Field("problem_id", "reference problem"),
                Field("handle"))

db.define_table("atcoder_problems",
                Field("problem_identifier"),
                Field("contest_id"),
                Field("name"))

db.define_table("problem_recommendations",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                # The possible states of a recommendation are:
                # 0 - Recommended, 1 - Viewed, 2 - Attempted, 3 - Solved
                Field("state", "integer", default=0),
                Field("is_active", "boolean"),
                Field("generated_at", "date"))

uvadb.define_table("problem",
                   Field("problem_id", "integer"),
                   Field("problem_num", "integer"),
                   Field("title"),
                   Field("problem_status", "integer"))

uvadb.define_table("usernametoid",
                   Field("username"),
                   Field("uva_id"))

if session["auth"]:
    session["handle"] = session["auth"]["user"]["stopstalk_handle"]
    session["user_id"] = session["auth"]["user"]["id"]

current.db = db
current.uvadb = uvadb

current.WEIGHTING_FACTORS = {
    "curr_day_streak": 40 * 10,
    "max_day_streak": 20 * 10,
    "solved": 1 * 23,
    "accuracy": 5 * 35,
    "attempted": 2 * 2,
    "curr_per_day": 1000 * 20
}
current.REFRESH_INTERVAL = 120 * 60

# ----------------------------------------------------------------------------
def get_static_file_version(file_path):
    if current.environment == "production":
        new_file_path = file_path
        static_dir = "static/minified_files"
        if file_path[-3:] == ".js":
            new_file_path = file_path[:-3] + ".min.js"
        elif file_path[-4:] == ".css":
            new_file_path = file_path[:-4] + ".min.css"
        else:
            static_dir = "static"
            new_file_path = file_path
    else:
        new_file_path = file_path
        static_dir = "static"

    return static_dir, new_file_path, current.REDIS_CLIENT.get(new_file_path)

# ----------------------------------------------------------------------------
def get_static_url(file_path):
    """
        Get the link to the minified static file with versioning
        @params file_path (String): Relative path of the static file

        @return (String): URL of the minified static resource with versioning
    """

    if current.environment == "production":
        static_dir, file_path, revision = get_static_file_version(file_path)
        return URL(static_dir,
                   file_path,
                   vars={"_rev": revision},
                   extension=False)
    else:
        return URL("static",
                   file_path,
                   extension=False)

current.get_static_file_version = get_static_file_version
current.get_static_url = get_static_url

# =============================================================================
