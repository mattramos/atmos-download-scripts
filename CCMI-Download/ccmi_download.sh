#!/bin/bash

HOME= # The directory where your .netrc file is 
export HOME

saveDir=$1
ftpDir=$2
file_name=$3

HOST='ftp.ceda.ac.uk'

cd $saveDir

ftp -i $HOST > /dev/null 2>&1 <<END_SCRIPT
binary
cd /badc/wcrp-ccmi/data/CCMI-1/output
cd $ftpDir
mget $file_name >/dev/null
quit
END_SCRIPT
exit 0 