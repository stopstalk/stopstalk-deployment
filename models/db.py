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
COLLEGES = ["ABES IT Group of Institutions, Ghaziabad",
            "ABV - Indian Institute of Information Technology and Management Gwalior",
            "AWH Engineering College, Calicut",
            "Abes Engineering college, Ghaziabad",
            "Acropolis Institute of Technology & Research, Indore",
            "Ajay Kumar Garg Engineering College, Ghaziabad",
            "Al Akhawayn University,  Ifrane",
            "Ambala College of Engineering and Applied Research, Ambala",
            "Ambedkar Institute of Advanced Communication Technology & Research",
            "Amity School of Engineering and Technology",
            "Amity University, Noida",
            "Amrita School of Engineering, Coimbatore",
            "Anil Neerukonda Institute of Technology and Sciences",
            "Appa Institute Of Engineering and Technology",
            "Army Institute of Technology, Pune",
            "Atharva College of Engineering , Malad",
            "B K Birla Institute of Engineering & Technology, Pilani",
            "B.V. Bhoomaraddi College of Engineering and Technology, Hubli",
            "BMS Institute of Technology, Bangalore",
            "Babasaheb Naik College of Engineering, Pusad",
            "Babu Banarasi Das Educational Society's Group of Institutions",
            "Baddi University of Emerging Sciences and Technologies",
            "Banasthali University",
            "Beijing University of Aeronautics and Astronautics",
            "Bhagwan Parshuram Institute of Technology",
            "Bharati Vidyapeeth College of Engineering, Delhi",
            "Birla Institute Of Technology, Mesra, Deoghar Campus",
            "Birla Institute of Technology & Science Pilani, Goa Campus",
            "Birla Institute of Technology & Science Pilani, Hyderabad Campus",
            "Birla Institute of Technology & Science Pilani, Pilani Campus",
            "Birla Institute of Technology Jaipur",
            "Birla Institute of Technology Mesra",
            "Birsa Institute of Technology, Sindri",
            "Budge Budge Institute of Technology, Calcutta"
            "Chandigarh College of Engineering & Technology",
            "Chandigarh University",
            "Charotar University of Science and Technology",
            "Cochin University of Science and Technology",
            "College of Engineering, Trivandrum",
            "College of Technology, Pantnagar",
            "Cummins College of Engineering for Women%",
            "Dhirubhai Ambani Institute of Information and Communication Technology",
            "Delhi Public School, Dwarka",
            "Delhi Public School, Faridabad",
            "Delhi Technological University",
            "Dhaneswar Rath Institute of Engineering and Management Studies, Cuttack",
            "Dharmsinh Desai University, Nadiad",
            "Dwarka International School, Dwarka",
            "Echelon Institute of Technology, Faridabad",
            "Fr. Conceicao Rodrigues College of Engineering, Bandra",
            "G. Narayanamma Institute of Technology and Science, Hyderabad",
            "GD Goenka University, Gurgaon",
            "GD Goenka World Institute",
            "GLA University, Mathura",
            "Galgotias College of Engineering and Technology",
            "Galgotias University",
            "Gautam Buddha University, Greater Noida",
            "Gokaraju Rangaraju Institute of Engineering and Technology, Hyderabad",
            "Goldman Sachs",
            "Government Engineering College, Thrissur",
            "Govind Ballabh Pant Engineering College, New Delhi",
            "Graphic Era University",
            "Guru Tegh Bahadur Institute of Technology, New Delhi",
            "HKBK College of Engineering, Bengaluru",
            "Haldia Institute of Technology, West Bengal",
            "Harcourt Butler Technological Institute, Kanpur",
            "Heritage Institute of Technology, Kolkata",
            "IMS Engineering College, Ghaziabad, Delhi NCR",
            "ITM University, Gwalior",
            "ITMO University",
            "Indian Institute of Engineering Science and Technology, Shibpur",
            "Indian Institute of Information Technology, Allahabad",
            "Indian Institute of Information Technology, Kolkata",
            "Indian Institute of Space Science and Technology, Thiruvananthapuram",
            "Indian Institute of Technology Bhubaneswar",
            "Indian Institute of Technology Guwahati",
            "Indian Institute of Technology Indore",
            "Indian Institute of Technology Kharagpur",
            "Indian Institute of Technology Madras",
            "Indian Institute of Technology Mandi",
            "Indian Institute of Technology Roorkee",
            "Indira Gandhi Delhi Technical University for Women",
            "Indraprastha Institute of Information Technology, Delhi",
            "Institute of Engineering & Management, Kolkata",
            "Institute of Engineering and Technology, Devi Ahilya Vishwavidyalaya",
            "Institute of Technical Education & Research, Bhubaneswar",
            "Institute of Technology, Nirma University",
            "Integral University",
            "International Institute of Information Technology, Bangalore",
            "International Institute of Information Technology, Hyderabad",
            "International Institute of Professional Studies, Indore",
            "JRE Group of Institutions, Greater Noida",
            "JSS Academy of Technical Education, Noida",
            "Jadavpur University",
            "Jamia Millia Islamia",
            "Jawaharlal Nehru Technological University, Kakinada",
            "Jawaharlal Nehru Technological University, Vizianagaram",
            "Jaypee Institute of Information Technology",
            "Jaypee University of Engineering and Technology, Guna",
            "Jaypee University of Information Technology",
            "Jodhpur Institute of Engineering & Technology",
            "K. J. Somaiya College of Engineering Vidyanagar, Vidyavihar, Mumbai",
            "KLS Gogte Institute of Technology, Belgaum",
            "Kalinga Institute of Industrial Technology",
            "Kalyani Government Engineering College",
            "Kamla Nehru Institute of Technology, Sultanpur, India",
            "Karpagam College of Engineering, Coimbatore",
            "Karunya University, Coimbatore",
            "Krishna Institute of Engineering and Technology, Ghaziabad",
            "LDRP Institute of Technology & Research, Gandhinagar",
            "LNM Institute of Information Technology",
            "Lal Bahadur Shastri Institute of Management, Delhi",
            "Lalbhai Dalpatbhai College of Engineering, Ahmedabad",
            "Lovely Professional University",
            "M. J. P. Rohilkhand University, Bareilly",
            "M. S. Ramaiah Institute of Technology, Bengaluru",
            "M.H. Saboo Siddik College of Engineering, Mumbai",
            "MIT Academy of Engineering, Pune",
            "Maharaja Agrasen Institute of Technology, New Delhi",
            "Maharaja Surajmal Institute of Technology",
            "Mahatma Gandhi Institute of Technology",
            "Malaviya National Institute of Technology, Jaipur",
            "Manipal Institute of Technology, Manipal",
            "Mar Athanasius College of Engineering, Kothamangalam",
            "Maulana Azad National Institute of Technology, Bhopal",
            "Motilal Nehru National Institute of Technology Allahabad",
            "Mugniram Bangur Memorial Engineering College, Jodhpur",
            "National Institute of Science and Technology, Berhampur",
            "National Institute of Technology Agartala",
            "National Institute of Technology Karnataka",
            "National Institute of Technology Mizoram",
            "National Institute of Technology Patna",
            "National Institute of Technology Raipur",
            "National Institute of Technology Tiruchirappalli",
            "National Institute of Technology, Calicut",
            "National Institute of Technology, Durgapur",
            "National Institute of Technology, Hamirpur",
            "National Institute of Technology, Jalandhar",
            "National Institute of Technology, Jamshedpur",
            "National Institute of Technology, Kurukshetra",
            "National Institute of Technology, Nagaland",
            "National Institute of Technology, Puducherry",
            "National Institute of Technology, Silchar",
            "National Institute of Technology, Uttarakhand",
            "Netaji Subhas Institute of Technology, New Delhi",
            "New Digambar Public School Indore",
            "Noida Institute of Engineering and Technology",
            "Northern India Engineering College, New Delhi",
            "PES College of Engineering, Mandya",
            "PSG College of Technology, Coimbatore",
            "Padre Conceicao College of Engineering, Goa",
            "Pillai Institute of Information Technology, Engineering, Media Studies and Research, Panvel",
            "Pimpri Chinchwad College of Engineering, Pune",
            "Poornima College of Engineering, Jaipur",
            "Poornima Institute of Engineering and Technology, Sitapura",
            "Pranveer Singh Institute of Technology, Kanpur",
            "Prasad V Potluri Siddhartha Institute of Technology",
            "Pune Institute of Computer Technology",
            "Punjab Engineering College, Chandigarh",
            "RCC Institute of Information Technology, Kolkata",
            "RK University, Rajkot",
            "RMD Engineering College, Tamil Nadu",
            "RMK College of Engineering & Technology, Tiruvallur",
            "RMK Engineering College, Tamil Nadu",
            "Raghu Engineering College",
            "Rajdhani College, University of Delhi",
            "Rajiv Gandhi University of Knowledge Technologies, RK Valley",
            "Ramanujan College, University of Delhi",
            "Rashtreeya Vidyalaya College of Engineering, Bangalore",
            "Rustamji Institute of Technology",
            "SAI International School",
            "SRM University",
            "Sant Longowal Institute of Engineering and Technology",
            "Sardar Patel Institute Of Technology, Mumbai",
            "Shiv Nadar University, Chithera",
            "Shivaji College, Delhi",
            "Shri Govindram Seksaria Institute of Technology and Science",
            "Shri Mata Vaishno Devi University",
            "Shri Ramswaroop Memorial College of Engineering and Management",
            "Sir M Visveswaraya Institute of Technology, Bangalore",
            "Sir Padampat Singhania University, Udaipur",
            "Sri Manakula Vinayagar Engineering College",
            "Sri Shakthi Institute of Engineering and Technology",
            "Stanley College of Engineering and Technology",
            "Swami Keshvanand Institute of Technology Management & Gramothan",
            "Techno India Salt Lake",
            "Thakur College of Engineering and Technology",
            "Thangal Kunju Musaliar College of Engineering, Kollam",
            "Thapar University",
            "The Scindia School",
            "University Institute of Engineering & Technology, Panjab University",
            "University Institute of Information Technology, Shimla",
            "University of Petroleum and Energy Studies, Dehradun",
            "University of Pune",
            "University of Waterloo, Canada",
            "University School of Information Technology",
            "University Visvesvaraya College of Engineering, Bangalore",
            "VVP Engineering College, Rajkot",
            "Varvakio Piramatiko Gimnasio, Greece",
            "Vasavi College of Engineering",
            "Veer Surendra Sai University of Technology, Orissa",
            "Vellore Institute of Technology, Chennai",
            "Vellore Institute of Technology, Vellore",
            "Veltech Multi Tech Dr.Rangarajan Dr.Sakunthala Engineering College, Chennai",
            "Vishwakarma Government Engineering College, Chandkheda",
            "West Bengal University of Technology",
            "YMCA University of Science and Technology, Faridabad",
            "Zakir Hussain College of Engineering and Technology, Aligarh",
            "Other"]

extra_fields = [Field("institute",
                      requires=IS_IN_SET(COLLEGES,
                                         zero="Institute",
                                         error_message="Institute Required")),
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
                Field("allowed_cu", "integer",
                      default=3,
                      readable=False,
                      writable=False),
                Field("blacklisted",
                      default=False,
                      readable=False,
                      writable=False)]

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

# -----------------------------------------------------------------------------
def send_mail(to, subject, message):
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
                        Field("institute",
                              requires=IS_IN_SET(COLLEGES,
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
                Field("problem_name"),
                Field("tags",
                      default="['-']"),
                Field("problem_added_on", "date"))

db.define_table("contact_us",
                Field("name", requires=IS_NOT_EMPTY()),
                Field("email", requires=[IS_NOT_EMPTY(), IS_EMAIL()]),
                Field("phone_number", requires=IS_NOT_EMPTY()),
                Field("subject", requires=IS_NOT_EMPTY()),
                # @ToDo: Not working for some reason
                Field("text_message", "text", requires=IS_NOT_EMPTY()))

if session["auth"]:
    session["handle"] = session["auth"]["user"]["stopstalk_handle"]
    session["user_id"] = session["auth"]["user"]["id"]

current.db = db
