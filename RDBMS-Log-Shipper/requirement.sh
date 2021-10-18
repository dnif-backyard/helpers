#!/bin/bash

echo "Installing virtualenv"

wheel_path="$PWD/requirements/pip/"
pip3 install --no-index --find-links=file:"$wheel_path" virtualenv

echo "creating python3 instance rdbms_connector "
cd $PWD
virtualenv -p python3 .


#activate envirnoment
echo "activate virtualenv rdbms_connector"
source $PWD/bin/activate

echo "Installing required pip3 packages from requirements.txt "
pip3 install --no-index --find-links  "$wheel_path" -r $PWD/requirement.txt

apt_path="$PWD/requirements/apt"
if [[ ! -e /etc/unixODBC ]]; then
  cd $apt_path
  tar -zxvf unixODBC-2.3.4.tar.gz
  cd unixODBC-2.3.4
  ./configure --prefix=/usr --sysconfdir=/etc/unixODBC
  make
  make install
fi
