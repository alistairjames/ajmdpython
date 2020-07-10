#!/bin/bash

run_type='demo'

# Check if a 'demo' argument is supplied
if [ "$#" -eq 1 ]; then
    if [ "$1" == 'main' ]; then
      run_type='main'
    fi
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
  printf "\nRunning the app with the parameter \'${run_type}\' from %s\n\n" "$DIR"
  python -m candidates.candidates_main $run_type
else
  printf "Failed to work out the directory path for candidates.sh \n"
  printf "Try running as 'python -m candidates.candidates_main' from the CandidatesPython folder\n"
  exit 0
fi






