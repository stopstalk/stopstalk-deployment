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

atable = db.auth_user
iutable = db.institute_user

sql_query = """
SELECT send_to_id, GROUP_CONCAT(user_registered_id)
FROM institute_user
GROUP BY send_to_id;
"""
res = db.executesql(sql_query)
all_user_ids = set([])

for row in res:
    all_user_ids.add(row[0])
    for uid in row[1].split(','):
        all_user_ids.add(int(uid))

id_to_record = {}
rows = db(atable.id.belongs(all_user_ids)).select(atable.id,
                                                  atable.first_name,
                                                  atable.last_name,
                                                  atable.email,
                                                  atable.stopstalk_handle)
for row in rows:
    id_to_record[row.id] = row

def send_message(to_record, from_records):
    names = [str(A(x.first_name + " " + x.last_name,
                   _href=URL("user",
                             "profile",
                             args=x.stopstalk_handle,
                             scheme="https",
                             host="www.stopstalk.com",
                             extension=False))) for x in from_records]

    has_have = ""
    if len(from_records) == 1:
        subject = "Someone registered from your Institute"
        name_string = names[0]
        address_string = "him / her"
        has_have = "has"
    else:
        subject = "A few people registered from your Institute"
        name_string = ", ".join(names[:-1]) + " and " + names[-1]
        address_string = "them"
        has_have = "have"

    message = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" >
<title>StopStalk</title>
<link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,600,700" rel="stylesheet">
<style type="text/css">
html { -webkit-text-size-adjust: none; -ms-text-size-adjust: none;}

  @media only screen and (min-device-width: 750px) {
    .table750 {width: 750px !important;}
  }
  @media only screen and (max-device-width: 750px), only screen and (max-width: 750px){
      table[class="table750"] {width: 100% !important;}
      .mob_b {width: 93% !important; max-width: 93% !important; min-width: 93% !important;}
      .mob_b1 {width: 100% !important; max-width: 100% !important; min-width: 100% !important;}
      .mob_left {text-align: left !important;}
      .mob_soc {width: 50% !important; max-width: 50% !important; min-width: 50% !important;}
      .mob_menu {width: 50% !important; max-width: 50% !important; min-width: 50% !important; box-shadow: inset -1px -1px 0 0 rgba(255, 255, 255, 0.2); }
      .mob_center {text-align: center !important;}
      .top_pad {height: 15px !important; max-height: 15px !important; min-height: 15px !important;}
      .mob_pad {width: 15px !important; max-width: 15px !important; min-width: 15px !important;}
      .mob_div {display: block !important;}
  }
   @media only screen and (max-device-width: 550px), only screen and (max-width: 550px){
      .mod_div {display: block !important;}
   }
  .table750 {width: 750px;}
</style>
</head>
<body style="margin: 0; padding: 0;">

<table cellpadding="0" cellspacing="0" border="0" width="100%" style="background: #f3f3f3; min-width: 350px; font-size: 1px; line-height: normal;">
  <tr>
    <td align="center" valign="top">        
      <!--[if (gte mso 9)|(IE)]>
         <table border="0" cellspacing="0" cellpadding="0">
         <tr><td align="center" valign="top" width="750"><![endif]-->
      <table cellpadding="0" cellspacing="0" border="0" width="750" class="table750" style="width: 100%; max-width: 750px; min-width: 350px; background: #f3f3f3;">
        <tr>
               <td class="mob_pad" width="25" style="width: 25px; max-width: 25px; min-width: 25px;">&nbsp;</td>
          <td align="center" valign="top" style="background: #ffffff;">

                  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="width: 100% !important; min-width: 100%; max-width: 100%; background: #f3f3f3;">
                     <tr>
                        <td align="right" valign="top">
                           <div class="top_pad" style="height: 25px; line-height: 25px; font-size: 23px;">&nbsp;</div>
                        </td>
                     </tr>
                  </table>

                  <table cellpadding="0" cellspacing="0" border="0" width="88%" style="width: 88% !important; min-width: 88%; max-width: 88%;">
                     <tr>
                        <td align="left" valign="top">
                           <div style="height: 39px; line-height: 39px; font-size: 37px;">&nbsp;</div>
                           <a href="#" target="_blank" style="display: block; max-width: 128px;">
                              <img src="img/stopstalk.png" alt="img" width="128" border="0" style="display: block; width: 128px;" />
                           </a>
                           <div style="height: 73px; line-height: 73px; font-size: 71px;">&nbsp;</div>
                        </td>
                     </tr>
                  </table>

                  <table cellpadding="0" cellspacing="0" border="0" width="88%" style="width: 88% !important; min-width: 88%; max-width: 88%;">
                     <tr>
                        <td align="left" valign="top">
                           <font face="'Source Sans Pro', sans-serif" color="#1a1a1a" style="font-size: 52px; line-height: 60px; font-weight: 300; letter-spacing: -1.5px;">
                              <span style="font-family: 'Source Sans Pro', Arial, Tahoma, Geneva, sans-serif; color: #1a1a1a; font-size: 52px; line-height: 60px; font-weight: 300; letter-spacing: -1.5px;">Hey %s,</span>
                           </font>
                           <div style="height: 33px; line-height: 33px; font-size: 31px;">&nbsp;</div>
                           <font face="'Source Sans Pro', sans-serif" color="#585858" style="font-size: 24px; line-height: 32px;">
                              <span style="font-family: 'Source Sans Pro', Arial, Tahoma, Geneva, sans-serif; color: #585858; font-size: 24px; line-height: 32px;">%s from your Institute %s just joined StopStalk.</span>
                           </font>
                           <div style="height: 20px; line-height: 20px; font-size: 18px;">&nbsp;</div>
                           <font face="'Source Sans Pro', sans-serif" color="#585858" style="font-size: 24px; line-height: 32px;">
                              <span style="font-family: 'Source Sans Pro', Arial, Tahoma, Geneva, sans-serif; color: #585858; font-size: 24px; line-height: 32px;">Add him / her as your friend now for better experience on StopStalk.”</span>

                              <p>Adjust your email preferences <a href="%s">here</a></p>
                           </font>
                           
                           <div style="height: 33px; line-height: 33px; font-size: 31px;">&nbsp;</div>
                           <table class="mob_btn" cellpadding="0" cellspacing="0" border="0" style="background: #27cbcc; border-radius: 4px;">
                              <tr>
                                 <td align="center" valign="top"> 
                                   
                                       <font face="'Source Sans Pro', sans-serif" color="#ffffff" style="font-size: 20px; line-height: 30px; text-decoration: none; white-space: nowrap; font-weight: 600;">
                                          <button style=" background-color: #4CAF50; /* Green */
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  "><a style="text-decoration: none;" href="http://www.stopstalk.com">Stop&nbsp;Stalk</a></button>
                                       </font>
                                    </a>
                                 </td>
                              </tr>
                           </table>
                           <div style="height: 75px; line-height: 75px; font-size: 73px;">&nbsp;</div>
                        </td>
                     </tr>
                  </table>

                  <table cellpadding="0" cellspacing="0" border="0" width="90%" style="width: 90% !important; min-width: 90%; max-width: 90%; border-width: 1px; border-style: solid; border-color: #e8e8e8; border-bottom: none; border-left: none; border-right: none;">
                     <tr>
                        <td align="left" valign="top">
                           <div style="height: 15px; line-height: 15px; font-size: 13px;">&nbsp;</div>
                        </td>
                     </tr>
                  </table>

                  <table cellpadding="0" cellspacing="0" border="0" width="88%" style="width: 88% !important; min-width: 88%; max-width: 88%;">
                     <tr>
                        <td align="center" valign="top">
                           <!--[if (gte mso 9)|(IE)]>
                           <table border="0" cellspacing="0" cellpadding="0">
                           <tr><td align="center" valign="top" width="50"><![endif]-->
                           <div style="display: inline-block; vertical-align: top; width: 50px;">
                              <table cellpadding="0" cellspacing="0" border="0" width="100%" style="width: 100% !important; min-width: 100%; max-width: 100%;">
                                 
                  </table>

                  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="width: 100% !important; min-width: 100%; max-width: 100%; background: #f3f3f3;">
                     <tr>
                        <td align="center" valign="top">
                           <div style="height: 34px; line-height: 34px; font-size: 32px;">&nbsp;</div>
                           <table cellpadding="0" cellspacing="0" border="0" width="88%" style="width: 88% !important; min-width: 88%; max-width: 88%;">
                             
      
</body>
</html>
""" % (to_record.stopstalk_handle,
       name_string,
       has_have,
       address_string,
       URL("default",
           "unsubscribe",
           scheme="https",
           host="www.stopstalk.com",
           extension=False))

    current.send_mail(to=to_record.email,
                      subject=subject,
                      message=message,
                      mail_type="institute_user",
                      bulk=True)

for row in res:
    send_message(id_to_record[row[0]],
                 [id_to_record[int(x)] for x in row[1].split(",")])

iutable.truncate()