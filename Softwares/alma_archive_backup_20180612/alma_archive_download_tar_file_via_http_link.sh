#!/bin/bash


# This script runs on Linux and MaxOS and downloads all the selected files to the current working directory in up to 5 parallel download streams.
# Should a download be aborted just run the entire script again, as partial downloads will be resumed. Please play nice with the download systems
# at the ARCs and do not increase the number of parallel streams.


if ! (command -v "wget" > /dev/null 2>&1 || command -v "curl" > /dev/null 2>&1); then
   echo "ERROR: neither 'wget' nor 'curl' are available on your computer. Please install one of them.";
   exit 1
fi

function start_session {
  if [[ -z "$ALMA_USERNAME" ]]; then export USERNAME="anonymous"; else export USERNAME="$ALMA_USERNAME"; fi #<Added><dzliu># 
  export AUTHENTICATION_STATUS=0
  if [ "${USERNAME}" != "anonymous" ]; then
    #echo ""
    #echo -n "Please enter the password for ALMA account ${USERNAME}: " > &2
    #read -s PASSWORD
    #echo ""
    export PASSWORD=$(python -c "import keyring; print(keyring.get_password('astroquery:asa.alma.cl','$USERNAME'))")
    # 
    if command -v "wget" > /dev/null 2>&1; then
      LOGINCOMMAND=(wget --quiet --delete-after --no-check-certificate --auth-no-challenge --keep-session-cookies --save-cookies alma-rh-cookie.txt "--http-user=${USERNAME}" "--http-password=${PASSWORD}")
    elif command -v "curl" > /dev/null 2>&1; then
      LOGINCOMMAND=(curl -s -k -o /dev/null -c alma-rh-cookie.txt "-u" "${USERNAME}:${PASSWORD}")
    fi
    # echo "${LOGINCOMMAND[@]}" "https://almascience.nrao.edu/dataPortal/api/login"
    $("${LOGINCOMMAND[@]}" "https://almascience.nrao.edu/dataPortal/api/login")
    AUTHENTICATION_STATUS=$?
    if [ $AUTHENTICATION_STATUS -eq 0 ]; then
      echo "            OK: credentials accepted."
    else
      echo "            ERROR: login credentials were wrong. Error code is ${AUTHENTICATION_STATUS}"
    fi
  fi
}

function end_session {
  rm -fr alma-rh-cookie.txt
}

function download {
  # wait for some time before starting - this is to stagger the load on the server (download start-up is relatively expensive)
  sleep $[ ( $RANDOM % 10 ) + 2 ]s

  if command -v "wget" > /dev/null 2>&1; then
    DOWNLOADCOMMAND=(wget -c -q -nv --no-check-certificate --auth-no-challenge --load-cookies alma-rh-cookie.txt)
  elif command -v "curl" > /dev/null 2>&1; then
    DOWNLOADCOMMAND=(curl -C - -s -k -O -f -b alma-rh-cookie.txt)
  fi

  echo "starting download of `basename $1`"
  $("${DOWNLOADCOMMAND[@]}" "$1")
  # echo "${DOWNLOADCOMMAND[@]}" "$1"
  STATUS=$?
  # echo "status ${STATUS}"
  if [ ${STATUS} -eq 0 ]; then
     echo "            succesfully downloaded `basename $1`"
     
  else
     echo "            ERROR downloading `basename $1`, error code is ${STATUS}"
  fi
}
export -f download

#echo "Downloading ${LIST} in up to 5 parallel streams. Total size is 7.9GB."
#echo "We now support resuming interrupted downloads - just re-run the script."
# tr converts spaces into newlines. Written legibly (spaces replaced by '_') we have: tr "\_"_"\\n"
# IMPORTANT. Please do not increase the parallelism. This may result in your downloads being throttled.
# Please do not split downloads of a single file into multiple parallel pieces.

start_session

if [ $AUTHENTICATION_STATUS -eq 0 ]; then
	#echo "your downloads will start shortly...."
	#echo ${LIST} | tr \  \\n | xargs -P1 -n1 -I '{}' bash -c 'download {};'
  for (( i=1; i<=$#; i++ )); do
      if [[ "${!i}" == "http"* ]]; then
          download "${!i}"
      fi
  done
fi
end_session
echo "Done."
