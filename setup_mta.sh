#!/bin/sh

#Keeping for future use, where the script can be used to run test case by passing the -t flag directly
: 'function argsHelp()
{
    echo -e "\n *** Usage help ***"
    echo -e "\n $0 [-t path/to/testcase.py] \n"
    exit 1
}
while getopts ":t:" flag
do
    case "$flag" in 
        t) testcase=${OPTARG} ;;
        :) argsHelp ;;
        \?) argsHelp ;;
    esac
done

#Check if t param is missing
if [ -z "$testcase" ]
then
    echo -e "\n ### Command line param -t missing. Please provide the test case to be executed ! ###"
    argsHelp
fi
'
#Build the mta docker image from dockerfile
docker build -t mta:latest dockerfiles/docker_fedora31/

#Run the mta container on port 8080 in detached mode
if [[ $(docker ps | grep windup_mta) = *windup_mta* ]]
then
    echo -e "\n MTA web console container is already running !"
else
    if [[ $(docker ps -a | grep windup_mta) = *windup_mta* ]]
    then
        echo -e "\n Starting the existing MTA web console docker container !"
        docker start windup_mta
    else
        echo -e "\n Starting new MTA web console container !"
        docker run -d -p 8080:8080 --name windup_mta -it mta:latest
    fi
fi

#Wait for mta web console to be fully up
echo -e "\n Waiting for mta web console to be available ..."
count=0
threshold=3
until $(curl --output /dev/null --silent --head --fail http://localhost:8080/mta-web); do
    if [ ${count} == ${threshold} ]
    then
      echo -e "\n Could not reach web console after all tries, exiting ..."
      exit 1
    fi
    echo ' \....\ '
    count=$(($count+1))
    sleep 10
done

echo -e "\n MTA web console is available now ! \n"

#Setup python3 virtual environment (version issue needs to be sorted)
python3.7 -m venv .mta_venv
source ./.mta_venv/bin/activate
pip install -e .

#Start selenium container
if [[ $(mta selenium status) == Running ]]
then
    echo -e "\n mta selenium container is already running !"
else
    echo -e "\n Starting mta selenium container !"
    mta selenium start
    sleep 10
fi

#Start tiger vnc viewer
mta selenium viewer

: 'echo -e '#!/bin/sh\n mta selenium viewer' > selenium-viewer.sh
chmod +x selenium-viewer.sh
./selenium-viewer.sh &
sleep 2

#Setup ftp(can be used, but need to handle passwords, hence skipping for now)

#Run the test(for future use)
#py.test $testcase

#Remove selenium-viewer file
#rm selenium-viewer.sh

#stop selenium (enable only if test is run via this script)
#mta selenium stop
'
