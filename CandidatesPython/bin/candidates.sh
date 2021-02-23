#!/bin/bash

run_type='undefined'
get_data=false

# if there is an argument provided, collect it
if [ "$#" -eq 1 ]; then
  if [ "$1" == 'demo' ]; then
    run_type='demo'
  elif [ "$1" == 'main' ]; then
    run_type='main'
    get_data=false
  elif [ "$1" == 'getdata_main' ]; then
    run_type='main'
    get_data=true
  fi
fi

if ! [[ $run_type =~  ^(demo|main|getdata_main)$  ]]; then
    echo "Instructions:"
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

if cd "${DIR}/.."; then
  printf "\nRunning with the parameter \'${run_type}\' from %s\n\n" "$DIR"
  if [ $get_data == true ]; then
    wget ftp://ftp.ebi.ac.uk/pub/databases/interpro/current/interpro.xml.gz -O data/main/input/interpro.xml.gz
    gunzip data/main/input/interpro.xml.gz
    wget ftp://ftp.ebi.ac.uk/pub/contrib/UniProt/UniFIRE/rules/unirule-urml-latest.xml -O data/main/input/unirule-urml-latest.xml
  fi
  python -m candidates.candidates_main $run_type
else
  printf "Failed to work out the directory path for candidates.sh \n"
  printf "Try running as 'python -m candidates.candidates_main' from the CandidatesPython folder\n"
  exit 0
fi







