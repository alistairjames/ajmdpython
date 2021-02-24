#!/bin/bash

run_type='undefined'
get_data=false

# if there is an argument provided, collect it
if [ "$#" -eq 1 ]; then
  if [ "$1" == 'test' ]; then
    run_type='test'
  elif [ "$1" == 'demo' ]; then
    run_type='demo'
  elif [ "$1" == 'main' ]; then
    run_type='main'
    get_data=false
  elif [ "$1" == 'getdata_main' ]; then
    run_type='main'
    get_data=true
  fi
fi

if ! [[ $run_type =~  ^(test|demo|main|getdata_main)$  ]]; then
    echo "Instructions:"
    echo "./candidates.sh test (runs the tests in the test folder with pytest)"
    echo "./candidates.sh demo (runs a short demo version on the data in data/demo/input)"
    echo "./candidates.sh main (runs the main program on the data in data/main/input)"
    echo "./candidates.sh getdata_main (collects the xml input data and runs the main program)"
    exit 0
fi

# Find the path to the directory of candidates.sh, go up one directory and then run the code
# https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

if ! cd "${DIR}/.."
then
  echo "Failed to move to the starting directory to run the script"
  exit
fi

# Create the output folders if they are missing
for dir in data/demo/output data/main/input data/main/output test/testdata/output
  do if [ ! -d $dir ]
     then
       mkdir $dir
     fi
done

# Move to the test folder and run the tests if $run_type is 'test'
if [ "$run_type" == "test" ]
then
  if cd "test"
  then
    echo "Running the tests with pytest"
    pytest
  else
    echo "Failed to move to the test folder to run the tests"
  fi
else
  printf "\nRunning with the parameter \'${run_type}\' from %s\n\n" "$DIR"
  if [ $get_data == true ]; then
    wget ftp://ftp.ebi.ac.uk/pub/databases/interpro/current/interpro.xml.gz -O data/main/input/interpro.xml.gz
    gunzip data/main/input/interpro.xml.gz
    wget ftp://ftp.ebi.ac.uk/pub/contrib/UniProt/UniFIRE/rules/unirule-urml-latest.xml -O data/main/input/unirule-urml-latest.xml
  fi
  python -m candidates.candidates_main $run_type
fi







