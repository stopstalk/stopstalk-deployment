git pull
python update_js_timestamp.py `cat STATIC_FILES`
restart uwsgi-emperor
touch /etc/uwsgi/web2py.xml
