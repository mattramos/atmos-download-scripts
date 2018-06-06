#!/bin/bash

HOME= # The directory where your .netrc file is
export HOME

HOST='ftp.ceda.ac.uk'

ftp -i $HOST <<END_SCRIPT
cd /badc/wcrp-ccmi/data/CCMI-1/output
ls -R ccmi_directory_list.txt
quit
END_SCRIPT
exit 0 