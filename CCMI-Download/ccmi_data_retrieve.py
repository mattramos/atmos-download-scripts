import os
import sys
import subprocess
import time
from ftplib import FTP

# --------------AUTHOR-----------------
# Matt Amos : m.amos1@lancaster.ac.uk
#
#
# --------------HISTORY----------------
# 8/3/18 MA Updated to download the latest version of the data, rather than
# the specified version, it will now download the latest version
# 9/3/18 MA Added statement to not redownload data
# 28/6/18 MA Fixed, so as not to download similarly named variables
#            e.g. not downloading vmro3s when vmro3 is selected
#
#
# --------------USE---------------------
# To download: python ccmi_data_retrieve.py download followed by
# exp = Experiment (e.g. refC1)
# o_freq = Output Frequency (e.g. mon)
# model_comp = Model Component (e.g. atmos)
# timestep = Time Step (e.g. monthly)
# real = Realisation (e.g. r1i1p1 or all)
# var_name Target variable name (e.g. vmro2)
# The final argument can be either 'overwrite' or 'refresh'
# or 'overwrite refresh'

# When pressed for an entry to create new file, just press ENTER

# Stripping down the entire tree structure of the CCMI directory
directory =  # USER SPECIFIED - directory where the program files can be found
data_dir =  # USER SPECIFIED - directory where the data is to be saved

ccmi_dir = "/badc/wcrp-ccmi/data/CCMI-1/output/"
ifilename = "ccmi_directory_list.txt"
ofilename = "ccmi_all_variable_paths.txt"
overwrite = False

# Get arguments
# ARG 1 is the method, aka which function to run
# ARG 2+ are the other variables
# If the last argument is 'refresh', 'overwrite' or 'overwrite refresh'
# then the script will refresh the database
try:
    arg_method = sys.argv[1]
except:
    print("No input argument!")
    sys.exit(1)
try:
    sys_arg = sys.argv[2:]
except:
    print("Not enough arguments")

# Refresh the files if the script is run
if sys_arg[-1] == "refresh":
    del sys_arg[-1]
    print('Starting file directory retrieval...')
    # Get the tree of the ftp server
    subprocess.call('./ccmi_filelist_retrieve.sh')
    print('File directory aquired')

    time.sleep(5)

    ifile = open(directory + ifilename, 'r')

    all_variable_path_names = []

    # Find all of the netcdf files present in the directory
    for line in ifile:
        if len(line.split('/')) == 9:
            current_dir = line.strip().strip(':') + "/"
        if line.strip()[-3:] == '.nc':
            fname = line.strip().split(' ')[-1]
            var_path = current_dir + fname
            all_variable_path_names.append(var_path)

    ofilename = "ccmi_all_variable_paths.txt"

    ofile = open(directory + ofilename, 'w')
    for var in all_variable_path_names:
        ofile.write("%s\n" % var)
    ofile.close()
elif sys_arg[-1] == "overwrite":
    del sys_arg[-1]
    overwrite = True
    print('Downloads will overwrite previous versions...')
    ifile = open(directory + ofilename, 'r')
    all_variable_path_names = []
    for line in ifile:
        all_variable_path_names.append(line.strip())
else:
    ifile = open(directory + ofilename, 'r')
    all_variable_path_names = []
    for line in ifile:
        all_variable_path_names.append(line.strip())

# Creates lists of all possible variables, models, etc
institutes = dict()
models = set()
experiments = set()
regimes = set()
timesteps = set()
realisations = set()
versions = set()
variables = set()
t = set()
mdl_vers = dict()

for path in all_variable_path_names:
    path = path.split('/')
    experiments.add(path[2])
    t.add(path[3])
    regimes.add(path[4])
    timesteps.add(path[5])
    realisations.add(path[6])
    variables.add(path[8])
    ver = path[7]
    versions.add(ver)
    mdl = path[1]
    institutes[mdl] = [path[0]]
    models.add(mdl)
    mdl_vers.setdefault(mdl, set()).add(ver)

# Find the latest version for each model, used for screen output
mdl_latest_vers = dict()
for mdl in mdl_vers:
    vers = mdl_vers[mdl]
    latest_ver = sorted(list(mdl_vers[mdl]))[-1]
    mdl_latest_vers[mdl] = latest_ver


def expand_timestep(mdl, exp, o_freq, model_comp, timestep, real, vers, var_name):
    # Expands the o_freq to allow for different timestep names

    time_list = []

    if 'mon' in o_freq:
        for o_freq in ['mon', 'monthly']:
            for timestep in ['mon', 'monthly']:
                time_list.append(
                    [mdl, exp, o_freq, model_comp, timestep, real, vers, var_name])

    if 'da' in o_freq:
        for o_freq in ['daily', 'day']:
            for timestep in ['daily', 'day']:
                time_list.append(
                    [mdl, exp, o_freq, model_comp, timestep, real, vers, var_name])

    return time_list


def find_var(mdl, exp, o_freq, model_comp, timestep, real, vers, var_name):
    # Finds the variable in all models
    # mdl = model (e.g. GEOSCCM)
    # exp = Experiment (e.g. refC1)
    # o_freq = Output Frequency (e.g. mon)
    # model_comp = Model Component (e.g. atmos)
    # timestep = Time Step (e.g. monthly)
    # real = Realisation (e.g. r1i1p1)
    # vers = Version (e.g. v1, all), this script will find the newest version data
    # var_name Target variable name (e.g. vmro2)

    path_list = []
    argslists = []

    # Accounts for multiple realisations, the ones that exist in the dataset
    if real == 'all':
        for temp_real in realisations:
            argslists += expand_timestep(mdl, exp, o_freq,
                                         model_comp, timestep,
                                         temp_real, vers, var_name)
    else:
        argslists += expand_timestep(mdl, exp, o_freq,
                                     model_comp, timestep, real,
                                     vers, var_name)

    # Check that the arglists created above are viable options
    for argslist in argslists:
        temp_path = '/'.join(institutes[argslist[0]] + argslist) + '/'
        path_list += [path for path in all_variable_path_names if temp_path in path]

    # if the path list is empty, check for previous versions, this is because
    # not all variables from a model have the same (latest) version
    if len(path_list) == 0:
        vers = 'v' + str(int(vers[1]) - 1)
        if vers != 'v0':
            path_list = find_var(mdl, exp, o_freq, model_comp,
                                 timestep, real, vers, var_name)

    return path_list


def download_var(exp, o_freq, model_comp, timestep, real, var_name):
    # Downloads the specified variable
    # exp = Experiment (e.g. refC1)
    # o_freq = Output Frequency (e.g. mon)
    # model_comp = Model Component (e.g. atmos)
    # timestep = Time Step (e.g. monthly)
    # real = Realisation (e.g. r1i1p1)
    # vers = Version (e.g. v1)
    # var_name Target variable name (e.g. vmro2)

    # Create directory if it doesn't exist
    var_path = '/'.join([exp, timestep, var_name])
    if not os.path.exists(data_dir + var_path):
        print("Creating new directory...")
        os.makedirs(data_dir + var_path)
        os.chdir(data_dir + var_path)
    else:
        os.chdir(data_dir + var_path)
        print("Directory already exists")

    mdl_count = 1
    mdl_num = len(models)
    for mdl in models:
        print('-----------Progress ' + str(mdl_count) +
              '/' + str(mdl_num) + '-----------')
        mdl_count += 1
        vers = mdl_latest_vers[mdl]
        print('The version of the data from ' + mdl + ' is: ' + vers)
        # Download the relevant data
        path_list = find_var(mdl, exp, o_freq, model_comp,
                             timestep, real, vers, var_name)

        L = len(path_list)
        i = 1
        for path in path_list:
            temp_path = '/'.join(path.split('/')[:-1])
            print('Downloading ' + str(i) + '/' +
                  str(L) + ': ' + path.split('/')[-1])
            file_name = path.split('/')[-1]
            # Check that the file doesn't already exist
            if not os.path.isfile(os.path.join(data_dir, var_path, file_name)) or overwrite:
                args = [data_dir + var_path, temp_path, file_name]
                command = [directory + 'ccmi_download.sh']
                command.extend(args)
                subprocess.call(command)
                i += 1
            else:
                print('File ' + file_name + ' already exists. SKIPPING...')
                i += 1


if arg_method == "download":
    if len(sys_arg) != 6:
        print("Incorrect number of arguments")
        sys.exit(1)
    exp = sys_arg[0]
    o_freq = sys_arg[1]
    model_comp = sys_arg[2]
    timestep = sys_arg[3]
    real = sys_arg[4]
    var_name = sys_arg[5]

    download_var(exp, o_freq, model_comp, timestep, real, var_name)
