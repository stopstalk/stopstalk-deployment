# StopStalk
Stop stalking and Start StopStalking :sunglasses:

## Module Requirements
Note: Apply sudo if required for your system.

Install the required packages by running:

```
pip install -r requirements.txt
```

## Installation
1. Install web2py in a directory
    * From source
    ```
    $ git clone --recursive https://github.com/web2py/web2py.git
    ```
    * From zip

        Directly [download](http://web2py.com/init/default/download) appropriate zip
        and unzip it to get the `web2py` directory set up on your local machine.

        Note: In this method you will have a fixed version of web2py, whereas in the former
              you might as well keep on pulling the latest changes made in web2py source.

   If you have it already jump to step 2.
2. Navigate into the applications directory in web2py directory.

    ```
    $ cd web2py/applications/
    ```
3. Install StopStalk by cloning this repository

    ```
    git clone https://github.com/stopstalk/stopstalk-deployment.git
    ```
4. Install MySQL - [here](http://dev.mysql.com/downloads/)
   Make sure you remember the root password for mysql server.

5. Create a database in MySQL

    ```
    $ mysql -u root -p        # Enter your mysql root password after this.

    mysql> CREATE DATABASE migration;
    ```
6. Copy `0firstrun.py` to `models/`

    ```
    $ cd applications/stopstalk
    $ cp models/0firstrun.py.sample models/0firstrun.py
    ```
7. Open `0firstrun.py` and change the settings.

    ```
    current.mysql_user = "root" # Change if you have given access to any other user in mysql
    current.mysql_password = "" # As per your mysql password
    current.mysql_server = "localhost"
    current.mysql_dbname = "migration" # Will remain same as long as you followed 5.

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
    ```

   In case if you want to send emails - Install `postfix` for your respective OS and configure the above smtp server accordingly.

8. Navigate back to the web2py folder and start the web2py server.

    ```
    $ cd web2py
    $ python web2py.py -a yourPassword // Choose any password
    ```

9. Open the browser and go to the URL -

    `http://localhost:8000/stopstalk/`

  **Note:**
  * The database will be completely empty after installation

10. Done. :smile:

## Contribute

1. Fork the repository
2. Clone your forked repository
3. Find any of the issues from here - [Issues] (https://github.com/stopstalk/stopstalk-deployment/issues) and try solving it
   or any other enhancements
4. Solve the bug or enhance the code and send a Pull Request!

   **Note:** Make sure to add the issue number in the commit message.

   Example Commit message: `Solved Issue #5`
5. We will review it as soon as possible.

## Configuration
    Configure the models/000_config.py file as per your requirement.

## Contact
  > Email: admin@stopstalk.com, contactstopstalk@gmail.com, raj454raj@gmail.com

  > Contact Us Page: https://www.stopstalk.com/contact_us

  > Creator Website: http://raj454raj.com

## Social Links

* [Facebook] (https://www.facebook.com/stopstalkcommunity/)
* [Twitter](https://twitter.com/stop_stalk)
* [Google-Plus](https://plus.google.com/110575194069678651985)
