A selection of scripts which downloads CCMI data from the BADC ftp server. Currently 
works on Unix systems. 

The files will be save in the specified directory/experiment/frequency/var_name

An example:

python ccmi_data_retrieve.py download refC1 mon atmos monthly all zmh2o2

Author : Matt Amos : m.amos1@lancaster.ac.uk

-------------------------------------------------------------------------------------------------------------------

Requirements to run:
1)  A .netrc file containing:

	machine ftp.ceda.ac.uk
    	login your_ceda_login
    	password your_ceda_password

    The .netrc file must have 700 permission (chmod 700 .netrc) and the file must be
    in the HOME directory

2)  Directories need to be updated in the files to run on your system

	ccmi_data_retrieve.py
	- directory (line 31) directory where the program files can be found
	- data_dir (line 32) directory where the data is to be saved
	
	ccmi_download.sh
	- HOME (line 3) the home directory (e.g. /home/usr/)

	ccmi_filelist_retrieve.sh
	- HOME (line 3) the home directory (e.g. /home/usr/)
	
-------------------------------------------------------------------------------------------------------------------

Arguments:

python ccmi_data_retrieve.py download exp o_freq model_comp timestep real var_name extras

After this in order

exp : experiment (refC1 etc)
o_freq : output frequency  from model (mon, day etc)
model_comp : model component (atmos)
timestep : the data timestep (monthly, daily etc)
real : realisation (r1i1p1, all etc)
var_name : variable name (vmro3, ta etc)
extras : (refresh, overwrite) explained below

These arguments match the directory structure and names on the CEDA server

-------------------------------------------------------------------------------------------------------------------

First Usage:
You must first run with refresh as the last argument: This will download the ccmi file 
	structure(~3mins) e.g.

python ccmi_data_retrieve.py download refC1SD mon atmos monthly all vmro3 refresh
	
Subsequent Usage: (EXAMPLES)

To download (not overwriting previous files)
python ccmi_data_retrieve.py download refC2 mon atmos montly r1i1p1 vmro3 

To download (overwriting previous files)
python ccmi_data_retrieve.py download refC2 mon atmos monthly all vmro3 overwrite

To download (not overwriting previous files), after refreshing the file database
python ccmi_data_retrieve.py download refC2 mon atmos monthly all vmro3 refresh

-------------------------------------------------------------------------------------------------------------------

Points to note
- You need to apply to access for the CCMI data
- The first time you run, you will need to run with 'refresh' as the last argument this
	may take a few minutes whilst the file structure is collected. It is stored so
	this process need only be repeated infrequently
- CESM models are not on BADC