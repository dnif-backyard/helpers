#!/bin/bash

echo "[-] Installing virtualenv"

setup_path=$PWD

wheel_path="$setup_path/requirements/pip/"
pip3 install --no-index --find-links=file:"$wheel_path" virtualenv

echo "[-] Creating python3 instance rdbms_connector"
cd $setup_path
virtualenv -p python3 .


#activate envirnoment
echo "[-] Activate virtualenv rdbms_connector"
source $setup_path/bin/activate

apt_path="$setup_path/requirements/apt"
if [[ ! -e /etc/unixODBC ]]; then
    echo "[-] Installing unixODBC"
    cd $apt_path
    tar -zxvf unixODBC-2.3.4.tar.gz
    cd unixODBC-2.3.4
    ./configure --prefix=/usr --sysconfdir=/etc/unixODBC
    make
    make install
fi

echo "[-] Installing required pip3 packages from requirements.txt "
pip3 install --no-index --find-links  "$wheel_path" -r $setup_path/requirement.txt

cd $apt_path

echo -e "[-] Checking for JDK \n"
if type -p java; then
    echo "[-] Java already installed"
elif [[ -n "$JAVA_HOME" ]] && [[ -x "$JAVA_HOME/bin/java" ]]; then
    echo "[-] Java already installed"
else
    echo "[-] Java not found"
    echo "[-] Installing Java"
    mkdir -p /usr/lib/jvm/
    wget https://download.java.net/java/GA/jdk14/076bab302c7b4508975440c56f6cc26a/36/GPL/openjdk-14_linux-x64_bin.tar.gz
    tar -xvf openjdk-14_linux-x64_bin.tar.gz -C /usr/lib/jvm/
    echo "export JAVA_HOME=/usr/lib/jvm/jdk-14">>/etc/profile.d/jdk14.sh
    echo "export PATH=\$PATH:\$JAVA_HOME/bin">>/etc/profile.d/jdk14.sh
    mkdir -p /usr/lib/jvm/java-14-openjdk-amd64
    cp -r /usr/lib/jvm/jdk-14/* /usr/lib/jvm/java-14-openjdk-amd64/
    source /etc/profile.d/jdk14.sh
    source /etc/profile
fi