#!/bin/bash
return_value=0
echo -e -n "\033[0m"
passed=0
failed=0
syntax_check_for_language() {
  while IFS= read -r line ; do
    # errors goes to stderr
    eval "$1 $line" > /dev/null
    if [ "$?" != "0" ]; then
      return_value=1;
      failed=$((failed+1))
      echo -e "$line \033[1;31m FAILED \033[0m"
    else
      passed=$((passed+1))
      echo -e "$line \033[1;32m OK \033[0m"
    fi
  done < <(git diff --name-only --staged | grep -E "\.$2$");
}
IFS=""
commands=("python -m py_compile@py" "bash -n@sh" "node -c@js")
for item in ${commands[*]}
do
  var1=$(echo $item | cut -f1 -d"@")
  var2=$(echo $item | cut -f2 -d"@")
  syntax_check_for_language "$var1" "$var2"
done 

echo -e "\nPassed: \033[1;32m$passed\033[0m"
echo -e "Failed: \033[1;31m$failed\033[0m"

exit $return_value
