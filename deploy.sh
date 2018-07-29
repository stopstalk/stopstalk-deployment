git pull
bash minify.sh `cat STATIC_FILES`
python update_js_timestamp.py `cat STATIC_FILES`
restart uwsgi-emperor
touch /etc/uwsgi/web2py.xml
