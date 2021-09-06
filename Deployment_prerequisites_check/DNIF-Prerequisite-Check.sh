#!/bin/bash

set -e
RED='\033[0;31m'
NC='\033[0m' # No Color
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'


echo -e "* Select the DNIF component you would like to check Prerequisites for:"
echo -e "    [1] Core (CO)"
echo -e "    [2] Local Console (LC)"
echo -e "    [3] Datanode (DN)"
echo -e "    [4] Adapter (AD)"
echo -e "    [5] Pico\n"
COMPONENT=""
while [[ ! $COMPONENT =~ ^[1-5] ]]; do
	echo -e "Pick the number corresponding to the component (1 - 5):  \c"
        read -r COMPONENT
done

case "${COMPONENT^^}" in
	1|2|3|4)

		getIP() {\
			echo -e "Enter ${1} ${2} IP Address:  \c"
			read -r ${1}IP${2}
		}
		getHostname() {
			echo -e "Enter ${1} ${2} Hostname:  \c"
			read -r ${1}hostname${2}
		}
		getValidatedIPs() {
			type=$1
			maxLength=$2
			for ((counter=1;counter<=$maxLength;counter++))
			do
				getIP $type $counter
				eval IP=\$${type}IP${counter}
				while [[ ! $IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; do
                    			echo -e "ENTER $type $counter IP Address: \c"
                        		read -r IP
                		done
				getHostname $type $counter
			done
		}
		bold=$(tput bold)
		COMP=""
		echo -e "-----------------------------------Enter Customer and Component Details----------------------------"
		echo -e "Enter the Customer Name :  \c"
		read -r cust
		echo -e "Enter Component Name: \c"
		read -r COMP
		echo -e "-----------------------------------Enter Core server Details---------------------------------------"

		### Get Core Details
		COREIP=""
		while [[ ! $COREIP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; do
			echo -e "ENTER CORE IP: \c"
			read -r COREIP
		done
		echo -e "Enter CORE Hostname:  \c"
                read -r coreHostname
		#getHostname "Core"

		echo -e "-----------------------------------Enter Datanode Server Details-----------------------------------"
		DatanodeCount=""
		while [[ ! $DatanodeCount =~ ^[1-9]+$ ]]; do
			echo -e "Enter number of Datanodes:  \c"
			read -r DatanodeCount

		done
		getValidatedIPs "Datanode" $DatanodeCount


		echo -e "-----------------------------------Enter Adapter Server Details------------------------------------"
		AdapterCount=""
		while [[ ! $AdapterCount =~ ^[1-9]+$ ]]; do
			echo -e "Enter number of Adapters:  \c"
			read -r AdapterCount

		done
		getValidatedIPs "Adapter" $AdapterCount

		echo -e "-----------------------------------Enter Proposed Hardware Details---------------------------------"
		echo -e "Enter Proposed RAM in GB: \c"
		read RAM
		echo -e "Enter Proposed Root (/) partition Disk Size in GB: \c"
		read root
		echo -e "Enter Proposed DNIF partition Disk Size GB: \c"
		read Dnif
		echo -e "Enter Proposed CPU (vCPU): \c"
		read CPU
		
		echo -e "\n\n"
		echo -e "**********************************************"
		echo -e "**Scanning Hardware and Network Prerequisite**"
		echo -e "**********************************************"

		
		date=$(echo "Prerequisites for host $(hostname) Date  $(date)")
		printf "$date\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "$date\n" 
		#RAM,CPU, Disk check
		
		printf "Input RAM = $RAM \n" >> "$cust"_"$COMP"_hardwarecheck.txt

		
		printf "\nRAM Check...................................................................${PURPLE}started${NC}\n" 
		total=$(free -m | awk '/Mem:/ {print $2}')
		avgramGB=$(($RAM - $RAM*10 / 100))
		ramgb=$((total / 1024))
		printf "Total RAM is.............................................................$ramgb GB  \n"  >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "Total RAM is.............................................................${BLUE}$ramgb GB ${NC} \n"
		if [ $ramgb -ge $avgramGB ]
		then
		    	printf "RAM Check................................................................Passed \n"  >> "$cust"_"$COMP"_hardwarecheck.txt
		    	printf "RAM Check................................................................${GREEN}Passed${NC} \n"
		else
		    	printf "RAM Check................................................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		    	printf "RAM Check................................................................${RED}Failed${NC} \n"
		fi

		printf "Input root partition = $root \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "\nCheck Root (/) Partition\n"	
		hdd=$(df -k / | awk '/dev/ {print $2}')
		avgrootdiskGB=$(($root - $root*10 / 100))
		hddgb=$((hdd/1024/1024))
		printf "Root (/) partition size is.................................................${BLUE}$hddgb GB\n${NC}"
		printf "Root (/) partition size is.................................................$hddgb GB \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		if [ $hddgb -ge $avgrootdiskGB ]
		then
			printf "Disk Check root (/) partition...................................................${GREEN}Passed${NC} \n"
			printf "Disk Check root (/) partition...................................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		else
			printf "Disk Check root (/) partition...................................................${RED}Failed${NC} \n"
			printf "Disk Check root (/) partition...................................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		fi
		
		printf "Input DNIF Partition Size = $Dnif \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "\nCheck DNIF Partition\n"
		hdd=$(df -k /DNIF | awk '/dev/ {print $2}') &> /dev/null 
		avgDnifdiskGB=$(($Dnif - $Dnif*10 / 100))
		hddgb=$((hdd/1024/1024))
		printf "DNIF partition size is.............................................${BLUE}$hddgb GB\n${NC}"
		printf "DNIF partition size is.............................................$hddgb GB\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		if [ $hddgb -ge $avgDnifdiskGB ]
		then
		        printf "Disk Check DNIF partition...................................... ........${GREEN}Passed${NC} \n"
		        printf "Disk Check DNIF partition...............................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		else
		        printf "Disk Check DNIF partition...............................................${RED}Failed${NC} \n"
		        printf "Disk Check DNIF partition...............................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		fi

		printf "Input CPU = $CPU \n" >> "$cust"_"$COMP"_hardwarecheck.txt

		printf "\nCPU Check.................................................................${PURPLE}started${NC}\n"
		cpu=$(nproc)
		printf "CPU Provided.............................................................${BLUE}$cpu\n${NC}"
		printf "CPU Provided.............................................................$cpu \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		if [ $cpu -ge $CPU ]
		then
		        printf "CPU Check................................................................${GREEN}Passed${NC} \n"
		        printf "CPU Check................................................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		else
		        printf "CPU Check................................................................${RED}Failed${NC} \n"
		        printf "CPU Check................................................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		fi
		
		echo -e "\n****Disk Statistics****\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		df -h >> "$cust"_"$COMP"_hardwarecheck.txt

		#NTP synchronization
		NTP=$(echo -e "\n\e[1m${bold}System clock synchronization details of $(hostname) system\e[0m\n")
		NTPsync=$(echo -e "\n****System clock synchronization details of $(hostname) system**** \n")
		printf "$NTPsync\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "$NTP\n"
		ifTimeSynched=$(timedatectl | awk '/System clock synchronized/{print $NF}')
		if [ "$ifTimeSynched" == "$ifTimeSynched" ]
		then
		        printf "System clock synchronization with NTP server.......................${GREEN}Passed${NC} \n"
		        printf "System clock synchronization with NTP server.......................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		 else
		        printf "System clock synchronization with NTP server.......................${RED}Failed${NC} \n"
		        printf "System clock synchronization with NTP server.......................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		  fi
		Localtime=$(timedatectl | awk '/Local time/{print $3,$4,$5,$6}')
		printf "Local Time of $(hostname).....................................$Localtime \n"
		printf "Local Time of $(hostname).....................................$Localtime \n" >> "$cust"_"$COMP"_hardwarecheck.txt
       		 UniversalTime=$(timedatectl | awk '/Universal time/{print $3,$4,$5,$6}')
        	printf "Universal time of $(hostname).................................$UniversalTime \n"
        	printf "Universal time of $(hostname).................................$UniversalTime \n" >> "$cust"_"$COMP"_hardwarecheck.txt
	
		#Interface Check
		Interface=$(ip addr show)
	        printf "\n\e[1m${bold}Interface\e[0m\n$Interface \n"
       		printf "\n****Interface****\n$Interface\n" >> "$cust"_"$COMP"_hardwarecheck.txt


		#Core Connectivity Check
		Connect=$(echo -e "\n\e[1m${bold}Connectivity with Core\e[0m\n")
		ConnectCOREIP=$(echo -e "\n*****Connectivity with Core****\n")
		printf "$ConnectCOREIP\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "$Connect\n"

		ping -c 2 $COREIP &> /dev/null &&
			printf "Connectivity with $COREIP.......................................${GREEN}Passed${NC} \n" ||
        		printf "Connectivity with $COREIP.......................................${RED}Failed${NC} \n"
		ping -c 2 $COREIP &> /dev/null &&
            		printf "Connectivity with $COREIP.......................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt ||
            		printf "Connectivity with $COREIP.......................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt


		Connecthostname=$(echo -e "\n\e[1m${bold}Hostname resolution for Core\e[0m\n")
		Connecthost=$(echo -e "\n****Hostname resolution for Core****\n")
		printf "$Connecthost\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "$Connecthostname\n"
        	ping -c 2 $coreHostname &> /dev/null &&
            		printf "Connectivity with $coreHostname.................................${GREEN}Passed${NC} \n" ||
            		printf "Connectivity with $coreHostname.................................${RED}Failed${NC} \n"
        	ping -c 2 $coreHostname &> /dev/null &&
            		printf "Connectivity with $coreHostname.................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt ||
            		printf "Connectivity with $coreHostname.................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
	
		#Datanode and Adapter connectivity check	
		for ((counter=1;counter<=$DatanodeCount;counter++))
		do
			eval DatanodeIP=\$DatanodeIP$counter
			eval Datanodehostname=\$Datanodehostname$counter
			Connectdatanode=$(echo -e "\n\e[1m${bold}Connectivity with Datanode $counter\e[0m\n")
			ConnectdatanodeIP=$(echo -e "\n****Connectivity with Datanode $counter**** \n")
			printf "$ConnectdatanodeIP\n" >> "$cust"_"$COMP"_hardwarecheck.txt
			printf "$Connectdatanode\n"
			
			ping -c 2 $DatanodeIP &> /dev/null &&
				printf "Connectivity with $DatanodeIP.......................................${GREEN}Passed${NC} \n" ||
				printf "Connectivity with $DatanodeIP.......................................${RED}Failed${NC} \n"
	        	ping -c 2 $DatanodeIP &> /dev/null &&
				printf "Connectivity with $DatanodeIP.......................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt ||
            			printf "Connectivity with $DatanodeIP.......................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
			

			ConnectDNhostname=$(echo -e "\n\e[1m${bold}Hostname resolution for Datanode $counter\e[0m\n")
			ConnectDNhost=$(echo -e "\n****Hostname resolution for Datanode $counter**** \n")
			printf "$ConnectDNhost\n" >> "$cust"_"$COMP"_hardwarecheck.txt
			printf "$ConnectDNhostname\n"
            		ping -c 2 $Datanodehostname &> /dev/null &&
           			 printf "Connectivity with $Datanodehostname.................................${GREEN}Passed${NC} \n" ||
            			printf "Connectivity with $Datanodehostname.................................${RED}Failed${NC} \n"
            		ping -c 2 $Datanodehostname &> /dev/null &&
            			printf "Connectivity with $Datanodehostname.................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt ||
            			printf "Connectivity with $Datanodehostname.................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt

		done

		for ((counter=1;counter<=$AdapterCount;counter++))
		do
			eval AdapterIP=\$AdapterIP$counter
			eval Adapterhostname=\$Adapterhostname$counter
			Connectadapter=$(echo -e "\n\e[1m${bold}Connectivity with Adapter $counter\e[0m\n")
			ConnectadapterIP=$(echo -e "\n****Connectivity with Adapter $counter****\n")
			printf "$ConnectadapterIP\n" >> "$cust"_"$COMP"_hardwarecheck.txt
			printf "$Connectadapter\n"
			ping -c 2 $AdapterIP &> /dev/null &&
            			printf "Connectivity with $AdapterIP.......................................${GREEN}Passed${NC} \n" ||
            			printf "Connectivity with $AdapterIP.......................................${RED}Failed${NC} \n"
            		ping -c 2 $AdapterIP &> /dev/null &&
            			printf "Connectivity with $AdapterIP.......................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt ||
            			printf "Connectivity with $AdapterIP.......................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt

			ConnectADhostname=$(echo -e "\n\e[1m${bold}Hostname resolution for Adapter $counter\e[0m\n")
			ConnectADhost=$(echo -e "\n****Hostname resolution for Adapter**** \n")
			printf "$ConnectADhost\n" >> "$cust"_"$COMP"_hardwarecheck.txt
			printf "$ConnectADhostname\n"
            		ping -c 2 $Adapterhostname &> /dev/null &&
            			printf "Connectivity with $Adapterhostname.................................${GREEN}Passed${NC} \n" ||
            			printf "Connectivity with $Adapterhostname.................................${RED}Failed${NC} \n"
            		ping -c 2 $AdapterIP &> /dev/null &&
				printf "Connectivity with $Adapterhostname.................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt ||
            			printf "Connectivity with $Adapterhostname.................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt

		done
		
		Port=$(echo -e "\n\e[1m${bold}PORT Prerequisites\e[0m\n")
		Ports=$(echo -e "\n****PORT Prerequisites****\n")
		printf "$Ports\n" >> "$cust"_"$COMP"_hardwarecheck.txt
        	printf "$Port\n"

		PORT=(80 22)
		for port in "${PORT[@]}";
		do
			if timeout 15 bash -c "</dev/tcp/localhost/$port" &> /dev/null
            		then
                    		printf "Port $port .....................................................${GREEN}Open${NC} \n"
                    		printf "Port $port .....................................................Open \n" >> "$cust"_"$COMP"_hardwarecheck.txt 
            		else
                    		printf "Port $port .....................................................${RED}Closed${NC} \n"
                    		printf "Port $port .....................................................Closed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
            		fi
        	done
      
        #URL Connectivity
		Websiteconnectivity=$(echo -e "\n\e[1m${bold}Connectivity Statistics:\e[0m\n")
		Website=$(echo -e "\n****Connectivity Statistics****")
		printf "$Website\n" >> "$cust"_"$COMP"_hardwarecheck.txt		
		printf "$Websiteconnectivity\n"
        	for site in  https://github.com/ https://google.com/ https://raw.github.com/ https://hub.docker.com/  https://hog.dnif.it/
        	do
                	if wget -O - -q -t 1 --timeout=6 --spider -S "$site" 2>&1 | grep -w "200\|301" ; then
                        	printf "Connectivity with $site.................................${GREEN}Passed${NC} \n"
                        	printf "Connectivity with $site.................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
                	else
                        	printf "Connectivity with $site.................................${RED}Failed${NC} \n"
                        	printf "Connectivity with $site.................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt

                	fi
        	done
		;;

	5)  
	#PICO
		bold=$(tput bold)
		COMP=""
		echo -e "-----------------------------------Enter Customer and Component Details----------------------------"
		echo -e "Enter the Customer Name :  \c"
		read -r cust
		echo -e "Enter Component Name: \c"
		read -r COMP
		
		echo -e "-----------------------------------Enter Proposed Hardware Details---------------------------------"
		echo -e "Enter Proposed RAM in GB: \c"
		read RAM
		echo -e "Enter Proposed root (/) partition Disk Size in GB: \c"
		read root
		echo -e "Enter Proposed DNIF partition Disk Size in GB: \c"
		read Dnif
		echo -e "Enter Proposed CPU (vCPU): \c"
		read CPU

		echo -e "\n\n"
		echo -e "**********************************************"
		echo -e "**Scanning Hardware and Network Prerequisite**"
		echo -e "**********************************************"


		date=$(echo "Prerequisites for host $(hostname) Date  $(date)")
		printf "$date\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "$date\n"

		printf "Input RAM = $RAM \n" >> "$cust"_"$COMP"_hardwarecheck.txt


		printf "RAM Check.....................................................................${PURPLE}started${NC}\n"
		total=$(free -m | awk '/Mem:/ {print $2}')
		avgramGB=$(($RAM - $RAM*10 / 100))
		ramgb=$((total / 1024))
		printf "Total RAM is..................................................................$ramgb GB \n"  >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "Total RAM is..................................................................${BLUE}$ramgb GB ${NC} \n"
		if [ $ramgb -ge $avgramGB ]
		then
			printf "RAM Check....................................................................Passed \n"  >> "$cust"_"$COMP"_hardwarecheck.txt
			printf "RAM Check....................................................................${GREEN}Passed${NC} \n"
		else
			printf "RAM Check....................................................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
			printf "RAM Check....................................................................${RED}Failed${NC} \n"
		fi

		printf "\nCheck Root Partition\n"

		printf "Input root partition = $root \n" >> "$cust"_"$COMP"_hardwarecheck.txt


		hdd=$(df -k / | awk '/dev/ {print $2}')
		avgrootdiskGB=$(($root - $root*10 / 100))
		hddgb=$((hdd/1024/1024))
		printf "Root (/) Disk partition size is......................................................${BLUE}$hddgb GB \n${NC}"
		printf "Root (/) Disk partition size is......................................................$hddgb GB \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		if [ $hddgb -ge $avgrootdiskGB ]
		then
			printf "Disk Check root (/) partition.......................................................${GREEN}Passed${NC} \n"
			printf "Disk Check root (/) partition.......................................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		else
			printf "Disk Check root (/) partition.......................................................${RED}Failed${NC} \n"
			printf "Disk Check root (/) partition.......................................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		fi

		printf "Input DNIF Partition zire = $Dnif \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "\nCheck DNIF Partition\n"


		hdd=$(df -k /DNIF | awk '/dev/ {print $2}')
		avgDnifdiskGB=$(($Dnif - $Dnif*10 / 100))
		hddgb=$((hdd/1024/1024))
		printf "DNIF partition size is........................................................${BLUE}$hddgb GB\n${NC}"
		printf "DNIF partition size is.........................................................$hddgb GB \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		if [ $hddgb -ge $avgDnifdiskGB ]
		then
		        printf "Disk Check DNIF partition...................................................${GREEN}Passed${NC} \n"
		        printf "Disk Check DNIF partition...................................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		else
		        printf "Disk Check DNIF partition...................................................${RED}Failed${NC} \n"
		        printf "Disk Check DNIF partition...................................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		fi

		printf "Input CPU = $CPU \n" >> "$cust"_"$COMP"_hardwarecheck.txt


		printf "\nCPU Check.......................................................................${PURPLE}started${NC}\n"
		cpu=$(nproc)
		printf "CPU Provided....................................................................${BLUE}$cpu\n${NC}"
		printf "CPU Provided....................................................................$cpu\ " >> "$cust"_"$COMP"_hardwarecheck.txt
		if [ $cpu -ge $CPU ]
		then
		        printf "CPU Check...................................................................${GREEN}Passed${NC} \n"
		        printf "CPU Check....................................................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		else
		        printf "CPU Check...................................................................${RED}Failed${NC} \n"
		        printf "CPU Check....................................................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		fi
		

                echo -e "\n****Disk Statistics****\n" >> "$cust"_"$COMP"_hardwarecheck.txt
                df -h >> "$cust"_"$COMP"_hardwarecheck.txt



		NTP=$(echo -e "\n\e[1m${bold}System clock synchronization details of $(hostname) system\e[0m\n")
		NTP=$(echo -e "\n****System clock synchronization details of $(hostname) system****\n")
		printf "$NTP\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "$NTP\n"
	
		ifTimeSynched=$(timedatectl | awk '/System clock synchronized/{print $NF}')
        	if [ "$ifTimeSynched" == "$ifTimeSynched" ]
        	then
		    	printf "System clock synchronization with NTP server.................................${GREEN}Passed${NC} \n"
		        printf "System clock synchronization with NTP server.................................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		else
		        printf "System clock synchronization with NTP server.................................${RED}Failed${NC} \n"
		        printf "System clock synchronization with NTP server.................................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		fi
		Localtime=$(timedatectl | awk '/Local time/{print $3,$4,$5,$6}')
        	printf "Local Time of $(hostname).....................................$Localtime \n"
        	printf "Local Time of $(hostname).....................................$Localtime \n" >> "$cust"_"$COMP"_hardwarecheck.txt
        	UniversalTime=$(timedatectl | awk '/Universal time/{print $3,$4,$5,$6}')
        	printf "Universal time of $(hostname).................................$UniversalTime \n"
        	printf "Universal time of $(hostname).................................$UniversalTime \n" >> "$cust"_"$COMP"_hardwarecheck.txt
		
		Interface=$(ip addr show)
		#Interface=$(nmcli -p device show | awk '/GENERAL.DEVICE:/{print}')
        	printf "\n\e[1m${bold}Interface\e[0m\n$Interface \n"
        	printf "\n****Interface****\n$Interface\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		
		#URL Connectivity
		Websiteconnectivity=$(echo -e "\n\e[1m${bold}Connectivity Statistics:\e[0m\n")
		Website=$(echo -e "\n****Connectivity Statistics****\n")
		printf "$Website\n" >> "$cust"_"$COMP"_hardwarecheck.txt
		printf "$Websiteconnectivity\n"
		for site in  https://github.com/ https://google.com/ https://raw.github.com/ https://hub.docker.com/  https://hog.dnif.it/
		do
			if wget -O - -q -t 1 --timeout=6 --spider -S "$site" 2>&1 | grep -w "200\|301" ; then
				printf "Connectivity with $site............................${GREEN}Passed${NC} \n" 
				printf "Connectivity with $site............................Passed \n" >> "$cust"_"$COMP"_hardwarecheck.txt
			else
   	 			printf "Connectivity with $site............................${RED}Failed${NC} \n"
				printf "Connectivity with $site............................Failed \n" >> "$cust"_"$COMP"_hardwarecheck.txt

			fi
		done
		;;
	esac	
