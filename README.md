# StopStalk
Stop stalking and Start StopStalking :sunglasses:

## Module Requirements
Note: Apply sudo if required for your system.

1. First make sure the development packages of libxml2 and libxslt are installed

Assuming you are running a Debian-based distribution, you can install them by using:

```
apt-get install python-dev libxml2-dev libxslt1-dev zlib1g-dev
```

Install the required packages by running:

```
pip install -r requirements.txt
```

Also, pip doesn't respect proxy while installing packages from requirements file. So if you are using proxy in your terminal you MAY use:

```
pip install -r requirements.txt --proxy=<proxy address>
```

2. To deploy the code, uglify-js and uglifycss needs to be installed

To install uglifyjs:
```
npm install uglify-js -g
```

To install uglifycss:
```
npm install uglifycss -g
```

## Installation
1. Install web2py (We need 2.14.6 version only) in a directory. We have commited the web2py source so that you can directly unzip and start using it

    * Unzip the web2py_src.zip somewhere outside the stopstalk directory.
    * After unzipping the web2py, copy the source of stopstalk to its applications directory
    * Final directory structure should be something like -
      - web2py/
        - applications/
          - stopstalk/
            - models
            - views
            - controllers
            - ...

2. Navigate into the applications directory in web2py directory.

    ```
    $ cd web2py/applications/
    ```
3. Install StopStalk by cloning this repository

    ```
    git clone https://github.com/stopstalk/stopstalk-deployment.git
    mv stopstalk-deployment stopstalk
    ```
    Note: Web2Py does not allow appname to contain hyphens.
4. Install MySQL - [here](http://dev.mysql.com/downloads/)
   Make sure you remember the root password for mysql server.

5. Create a database in MySQL

    ```
    $ mysql -u root -p        # Enter your mysql root password after this.

    mysql> CREATE DATABASE stopstalkdb;
    mysql> CREATE DATABASE uvajudge;
    ```
6. Copy `0firstrun.py` to `models/`

    ```
    $ cd stopstalk/
    $ cp models/0firstrun.py.sample models/0firstrun.py
    ```
7. Open `0firstrun.py` and change the settings.

    ```python
    current.mysql_user = "root" # Change if you have given access to any other user in mysql
    current.mysql_password = "" # As per your mysql password
    current.mysql_server = "localhost"
    current.mysql_dbname = "migration" # Will remain same as long as you followed 5.
    current.mysql_uvadbname = "uvajudge" # Will remain same as long as you followed 5.

    # Configure mail options
    current.smtp_server = "logging" # Mails will not be sent. Will be logged where the web2py server is running
                                    # Else you can set it to your smtp server.
    current.sender_mail = ""        # Not required if logging
    current.sender_password = ""    # Not required if logging

    current.bulk_smtp_server = "logging"
    current.bulk_sender_mail = ""        # Not required if logging
    current.bulk_sender_password = ""    # Not required if logging

    current.analytics_id = "" # Leave it empty if you don't want Google Analytics on Localhost
    current.calendar_token = "" # Leave it empty if you don't have an access token ID for Google Calendar API

    # Leave the following empty for very basic email validation
    # https://app.neverbounce.com/settings/api
    current.neverbounce_user = ""
    current.neverbounce_password = ""
    ```

   In case if you want to send emails - Install `postfix` for your respective OS and configure the above smtp server accordingly.

8. Install Redis - [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)

9. Install InfluxDB (1.7) - [here](https://docs.influxdata.com/influxdb/v1.7/introduction/installation/)

10. Navigate back to the web2py folder and start the web2py server.

    ```
    $ cd web2py
    $ python web2py.py -a yourPassword // Choose any password
    ```

11. Open the browser and go to the URL -

    `http://localhost:8000/stopstalk/`

  **Note:**
  * The database will be completely empty after installation

12. Done. :smile:

13. To setup syntax check before all of your commits, just create a file in applications/stopstalk/.git/hooks/pre-commit with just `make` as it's content.
 
A few steps to setup your local database - [StopStalk Wiki](https://github.com/stopstalk/stopstalk-deployment/wiki/Setup-basic-database-tables-locally)

## Project Dependencies

StopStalk is built on the [Web2Py Framework](http://www.web2py.com), which is a Python based MVC framework.
The project also depends on a number of other open source packages, some of which are

- [MySQL](http://www.mysql.com)
- [Redis](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)
- [Google Calender API](https://developers.google.com/google-apps/calendar/)
- [Google Charts API](https://developers.google.com/chart/)
- [Python Requests Library](http://docs.python-requests.org/en/master/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)

## Contribute

1. Fork the repository
2. Clone your forked repository
3. Find any of the issues from here - [Issues](https://github.com/stopstalk/stopstalk-deployment/issues) and try solving it
   or any other enhancements
4. Solve the bug or enhance the code and send a Pull Request!

   **Note:** Make sure to add the issue number in the commit message.

   Example Commit message: `Solved Issue #5`
5. We will review it as soon as possible.

## Configuration
    Configure the models/000_config.py file as per your requirement.

### Configuring Calendar API client ID

1. Goto [Google developers console](https://console.developers.google.com/) and click on New Project.
2. Give the project a name like stopstalk-test and create the project.
3. Goto API Manager.
4. Search and select Google Calendar API and enable it.
5. Click on Go To Credentials and fill out the form
6. Copy client ID and paste it in models/0firstrun.py
7. Done. :smile:

## Contact
  > Contact Us Page: https://www.stopstalk.com/contact_us

  > Email: admin@stopstalk.com, contactstopstalk@gmail.com, raj454raj@gmail.com

  > Creator Website: http://raj454raj.me

## Social Links

* [Facebook](https://www.facebook.com/stopstalkcommunity/)
* [Facebook Group](https://www.facebook.com/groups/stopstalk/)
* [Twitter](https://twitter.com/stop_stalk)
* [Google-Plus](https://plus.google.com/110575194069678651985)
