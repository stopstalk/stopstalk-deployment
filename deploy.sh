git pull
python update_js_timestamp.py `cat JSFILES`
restart uwsgi-emperor
touch /etc/uwsgi/web2py.xml
