#!/bin/bash

command_to_execute=$1

eval $command_to_execute
exit_code=`echo $?`
if [[ $exit_code -ne 0 ]]; then
  mail -s "[`hostname`] - Command failed: $command_to_execute, Exit code: " raj454raj@gmail.com <<< "Nothing"
fi
