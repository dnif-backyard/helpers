#!/bin/bash

echo "Installing virtualenv"

setup_path=$PWD

wheel_path="$setup_path/requirements/pip/"
pip3 install --no-index --find-links=file:"$wheel_path" virtualenv

echo "creating python3 instance rdbms_connector "
cd $setup_path
virtualenv -p python3 .


#activate envirnoment
echo "activate virtualenv rdbms_connector"
source $setup_path/bin/activate

apt_path="$setup_path/requirements/apt"
if [[ ! -e /etc/unixODBC ]]; then
  cd $apt_path
  tar -zxvf unixODBC-2.3.4.tar.gz
  cd unixODBC-2.3.4
  ./configure --prefix=/usr --sysconfdir=/etc/unixODBC
  make
  make install
fi

echo "Installing required pip3 packages from requirement.txt"
pip3 install --no-index --find-links  "$wheel_path" -r $setup_path/requirement.txt