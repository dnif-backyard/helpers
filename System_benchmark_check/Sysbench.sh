#!/bin/bash

#Color define
RED='\033[0;31m'
NC='\033[0m' # No Color
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'

#Bench Folder Creation
printf "${BLUE}$(date) ${YELLOW}Verifying /DNIF directory is created.........................${NC} \n"
#printf "$(date) Checking /DNIF directory is created..............................\n" >> /DNIF/Benchsystem/Sysbench.log
if [ -d "/DNIF" ] 
then
    printf "${BLUE}$(date) ${GREEN}/DNIF directory is exists....................................${NC} \n"
    mkdir -p /DNIF/Benchsystem/
    printf "$(date) /DNIF directory is exists..............................\n" >> /DNIF/Benchsystem/Sysbench.log
else
    printf "${BLUE}$(date) ${RED}/DNIF directory does not exist..............................${NC} \n"
    #printf "$(date) Checking /DNIF directory does not exist..............................\n" >> /DNIF/Benchsystem/Sysbench.log
    exit 126
fi

#mkdir -p /DNIF/Benchsystem/
#printf "${BLUE}$(date) ${GREEN}Sysbench Folder creation completed...........................${NC} \n"
#printf "$(date) Sysbench Folder creation completed...........................\n" >> /DNIF/Benchsystem/Sysbench.log
#Sysbench installation process
printf "${BLUE}$(date) ${PURPLE}Sysbench installation check begins...........................${NC} \n"
dpkg -s sysbench &> /dev/null  

if [ $? -ne 0 ]
then
	printf "$(date) Sysbench not installed \n" >> /DNIF/Benchsystem/Sysbench.log
        printf "${BLUE}$(date) ${RED}Sysbench not installed${NC} \n"
        sleep 1
        printf "${BLUE}$(date) ${YELLOW}Sysbench installation started${NC} \n"
        printf "$(date) Sysbench installation started \n" >> /DNIF/Benchsystem/Sysbench.log
	if [  -n "$(uname -a | grep Ubuntu)" ]; then
		#sudo apt-get update && sudo apt-get upgrade
		dpkg -i ./*.deb > /dev/null 2>&1
		vers=$(sysbench --version | awk '{print $2}')
		dpkg -s sysbench &> /dev/null
		if [ $? -ne 0 ]
		then
			printf "${BLUE}$(date) ${RED}Sysbench cannot be installed${NC} \n"
			exit 126
		else
			printf "${BLUE}$(date) ${GREEN}Sysbench Installed ............................${YELLOW}Version $vers${NC} \n"
			printf "$(date) Sysbench Installed ............................Version $vers \n" >> /DNIF/Benchsystem/Sysbench.log
		fi
	else
		#yum update
		curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.rpm.sh | sudo bash > /dev/null 2>&1
		sudo yum -y install sysbench > /dev/null 2>&1
		if [ $? -ne 0 ]
                then
                        printf "${BLUE}$(date) ${RED}Sysbench cannot be installed${NC} \n"
                        exit 126
                else
                        vers=$(sysbench --version | awk '{print $2}')
			printf "${BLUE}$(date) ${GREEN}Sysbench Installed ............................${YELLOW}Version $vers${NC} \n"
                        printf "$(date) Sysbench Installed ............................Version $vers \n" >> /DNIF/Benchsystem/Sysbench.log
                fi
	fi
else
	printf "$(date) Sysbench already installed...................Version $vers \n" >> /DNIF/Benchsystem/Sysbench.log
fi
sleep 1
printf "${BLUE}$(date) ${PURPLE}Sysbench installation check Completed........................${NC} \n"
sleep 1
printf "${BLUE}$(date) ${PURPLE}Sysbench Started.............................................${NC} \n"
sleep 1
# CPU check begins
cputhread=$(lscpu | awk '/Thread/ {print $4}')
#echo $cputhread
printf "${BLUE}$(date) ${RED}CPU check begins${NC} \n" 
printf "$(date) CPU check begins \n" >> /DNIF/Benchsystem/Sysbench.log
printf "$(date) CPU check begins \n" >> /DNIF/Benchsystem/outputsysbench.txt
cpubench=$(cd /DNIF && sysbench --test=cpu --num-threads=$cputhread --cpu-max-prime=20000 run 2>/dev/null)
#echo $a
echo $cpubench >> /DNIF/Benchsystem/outputsysbench.txt
if [ $cputhread == 1 ]; then
	timecpu=$(echo $cpubench | awk '{print $43}') > /dev/null 2>&1
	eventcpu=$(echo $cpubench | awk '{print $48}') > /dev/null 2>&1
	epscpu=$(echo "$eventcpu $timecpu" | awk '{print $1 / $2}')
else
        timecpu=$(echo $cpubench | awk '{print $50}') > /dev/null 2>&1
        eventcpu=$(echo $cpubench | awk '{print $55}') > /dev/null 2>&1
        epscpu=$(echo "$eventcpu $timecpu" | awk '{print $1 / $2}')
fi
printf "${BLUE}$(date) ${GREEN}CPU test completed${NC} \n"
printf "${BLUE}$(date) ${PURPLE}CPU test output..........................Total time: ${YELLOW}$timecpu${NC} \n"
printf "${BLUE}$(date) ${PURPLE}........................................Total Event: ${YELLOW}$eventcpu${NC} \n"
printf "${BLUE}$(date) ${PURPLE}.....................................Events per sec: ${YELLOW}$epscpu${NC} \n"
printf "$(date) CPU test completed \n" >> /DNIF/Benchsystem/Sysbench.log
printf "$(date) CPU test completed \n" >> /DNIF/Benchsystem/outputsysbench.txt
sleep 1
#Memory check begins
printf "${BLUE}$(date) ${RED}Memory check begins${NC} \n"
printf "$(date) Memory check begins \n" >> /DNIF/Benchsystem/Sysbench.log
printf "$(date) Memory check begins \n" >> /DNIF/Benchsystem/outputsysbench.txt
membench=$(sysbench --test=memory --num-threads=$cputhread run 2>/dev/null)
echo $membench >> /DNIF/Benchsystem/outputsysbench.txt
if [ $cputhread == 1 ]; then
	memtotalop=$(echo $membench | awk '{print $50" "$51" "$52}') > /dev/null 2>&1
	memthrough=$(echo $membench | awk '{print $56" "$57}') > /dev/null 2>&1
else
	memtotalop=$(echo $membench | awk '{print $57" "$58" "$59}') > /dev/null 2>&1
        memthrough=$(echo $membench | awk '{print $63" "$64 }') > /dev/null 2>&1
fi
printf "${BLUE}$(date) ${GREEN}Memory check completed${NC} \n"
printf "${BLUE}$(date) ${GREEN}Memory check output${NC} \n"
printf "${BLUE}$(date) ${PURPLE}....................................Total Operations:${YELLOW}$memtotalop${NC} \n"
printf "${BLUE}$(date) ${PURPLE}..........................................Throughput:${YELLOW}$memthrough${NC} \n"
printf "$(date) Memory check completed \n" >> /DNIF/Benchsystem/Sysbench.log

#I/O check 
printf "${BLUE}$(date) ${PURPLE}IO check begins${NC}\n"
printf "$(date) IO check begins \n" >> /DNIF/Benchsystem/Sysbench.log
printf "$(date) IO check begins \n" >> /DNIF/Benchsystem/outputsysbench.txt
sleep 1
printf "${BLUE}$(date) ${RED}IO benchmark is preparing files${NC} \n"
printf "$(date) IO benchmark is preparing files \n" >> /DNIF/Benchsystem/Sysbench.log
cd /DNIF/Benchsystem/ && sysbench --test=fileio --file-total-size=1G prepare 2>/dev/null >> /DNIF/Benchsystem/Sysbench.log
printf "${BLUE}$(date) ${GREEN}IO benchmark file preparation is complete${NC} \n"
printf "$(date) IO benchmark file preparation is complete \n" >> /DNIF/Benchsystem/Sysbench.log
sleep 1
printf "${BLUE}$(date) ${RED}IO benchmark test begins${NC} \n"
printf "$(date) IO benchmark test begins \n">> /DNIF/Benchsystem/outputsysbench.txt
iobench=$(cd /DNIF/Benchsystem/ && sysbench --test=fileio --file-total-size=150M --file-test-mode=rndrw --max-requests=0 run 2>/dev/null)
echo $iobench >> /DNIF/Benchsystem/outputsysbench.txt
printf "${BLUE}$(date) ${GREEN}IO benchmark test completed${NC} \n"
readsio=$(echo $iobench | awk '{print $84" "$85}')
writeio=$(echo $iobench | awk '{print $86" "$87}')
fsyncio=$(echo $iobench | awk '{print $88" "$89}')
throughread=$(echo $iobench | awk '{print $91" "$92" "$93}')
throughwrite=$(echo $iobench | awk '{print $94" "$95" "$96}')
printf "${BLUE}$(date) ${GREEN}IO check output${NC} \n"
printf "${BLUE}$(date) ${PURPLE}....................................File Operations:${YELLOW}$readsio${NC} \n"
printf "${BLUE}$(date) ${PURPLE}....................................................${YELLOW}$writeio${NC} \n"
printf "${BLUE}$(date) ${PURPLE}....................................................${YELLOW}$fsyncio${NC} \n"
printf "${BLUE}$(date) ${PURPLE}....................................File Throughput:${YELLOW}$throughread${NC} \n"
printf "${BLUE}$(date) ${PURPLE}....................................................${YELLOW}$throughwrite${NC} \n"
printf "$(date) IO benchmark test completed \n">> /DNIF/Benchsystem/Sysbench.log
printf "$(date) IO benchmark test completed \n">> /DNIF/Benchsystem/outputsysbench.txt
sleep 1
printf "${BLUE}$(date) ${RED}IO benchmark cleanup begin${NC} \n"
printf "$(date) IO benchmark cleanup begin \n">> /DNIF/Benchsystem/Sysbench.log
cd /DNIF/Benchsystem/ && sysbench --test=fileio --file-total-size=150M cleanup 2>/dev/null >> /DNIF/Benchsystem/Sysbench.log
printf "${BLUE}$(date) ${GREEN}IO benchmark cleanup completed${NC} \n"
printf "$(date) IO benchmark cleanup completed \n">> /DNIF/Benchsystem/Sysbench.log
sleep 1
printf "${BLUE}$(date) ${PURPLE}IO check completed${NC} \n"
sleep 1
printf "$(date) IO check completed \n" >> /DNIF/Benchsystem/Sysbench.log
printf "$(date) IO check completed \n" >> /DNIF/Benchsystem/outputsysbench.txt
sleep 1
printf "${BLUE}$(date) ${PURPLE}Sysbench Completed...........................................${NC} \n"
printf "$(date) Sysbench Completed.......................................... \n" >> /DNIF/Benchsystem/Sysbench.log
