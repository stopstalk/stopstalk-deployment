total_iterations=100

# Edit this according to your local environment
web2py_directory="/home/www-data/web2py/"

web2py_file="web2py.py"
web2py_file=$web2py_directory$web2py_file

script_file="applications/stopstalk/private/scripts/submissions.py"
script_file=$web2py_directory$script_file

python_path=`which python`

for i in $(seq 0 $[$total_iterations - 1])
do
    cmd="$python_path $web2py_file -S stopstalk -M -R $script_file -A daily_retrieve $total_iterations $i"
    echo $cmd
    /home/www-data/web2py/applications/stopstalk/exit_code_handler.sh "$cmd"

    if [ $i != $[$total_iterations - 1] ]
    then
        sleep 5
    fi
done
