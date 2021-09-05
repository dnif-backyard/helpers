
Cluster deployment prerequisites check - Helper script 

This script will assist you to check the hardware and network prerequisites across your provisioned infra for DNIF components.
# In this script we will cover below points
1) Hardware prerequisites check.
   1) Provisioned RAM
   1) Provisioned CPU
   1) Provisioned Disk (Root and DNIF partition)
1) NTP synchronization
   1) Localtime
   1) UniversalTime
1) Network Interface check
1) Connectivity check between Core, Datanode and Adapter
1) Hostname resolution between Core, Datanode and Adapter
1) Inter component open port check
1) Connectivity check to domains: github.com, google.com, raw.github.com, hub.docker.com,hog.dnif.it.

# How to use this script
1) $ Unzip the DNIF-Prerequisites-Check-Script.zip file
1) $ bash DNIF-Prerequisite-Check.sh

## The script would required below inputs:
1) Customer name
1) Component name
1) Core Server IP
1) Core Server Hostname
1) Number of Datanode
1) Datanode IP
1) Datanode Hostname
1) Number of Adapter
1) Adapter IP
1) Adapter Hostname
1) DNIF Team Proposed RAM in GB’s
1) DNIF Team Proposed Root partition size in GB’s
1) DNIF Team Proposed DNIF partition size in GB’s
1) DNIF Team Proposed CPU (vcpu):

## Outcome
The output of this script will show you the status of hardware and network prerequisites as **passed** or **failed**. Also the script will create an additional file by the name specified within “Customer Name” and “Component Name” as  example: “Netmonastery\_Core\_hardwarecheck.txt

Kindly review the checks marked as **failed** and resolve the same with the help of your system or network administrators. Once all the checks are marked as **passed** you can consider prerequisites to be ready.




