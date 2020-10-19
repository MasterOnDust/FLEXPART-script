#!/usr/bin/env python
import argparse as ap
import os
import pandas as pd
import shutil
import sys
import f90nml
import json
import collections.abc

def write_namelist(params_dict,path):
    nml = f90nml.Namelist(params_dict)
    nml.end_comma = True
    nml.uppercase = True
    nml.write(path, force=True)

def write_pathnames(folderName, paths):
    """ Write pathnames file """

    with open(folderName + '/pathnames', 'w') as pn:
        pn.writelines('./options/\n')
        pn.writelines('./output/\n')
        pn.writelines('/\n')
        pn.writelines(paths['path_to_forcing'] + '\n')
        pn.writelines(paths['flexpart_input_path'] + '\n')
        pn.writelines('============================================')



def write_sbatct_file(jobscript_params,daterange, paths):
    date0 = daterange.tolist()[0].strftime("%Y%m%d")
    date1 = daterange.tolist()[-1].strftime("%Y%m%d")
    job_file = paths['abs_path'] + '/submit_flexpart.sh'
    with open(job_file, 'w') as fh:
        fh.writelines("#!/bin/bash\n")
        for option, setting in settings.items():
            fh.writelines("#SBATCH --{}={}\n".format(option,setting))
        fh.writelines("#SBATCH --job-name=FLEXPART_{}\n".format(date0))
        fh.writelines("#SBATCH --error={}/out_{}.err\n".format(paths['abs_path'],date0))
        fh.writelines("#SBATCH --output={}/out_{}.out\n".format(paths['abs_path'],date0))
        fh.writelines("#SBATCH --mail-type=FAIL\n")
        fh.writelines("#SBATCH --array=1-4")
        fh.writelines('set -o errexit\n')
        fh.writelines('set -o nounset\n')
        fh.writelines('module --quiet purge\n')

        fh.writelines('module load ecCodes/2.9.2-intel-2018b\n')
        fh.writelines('module load netCDF-Fortran/4.4.4-intel-2018b\n')
        fh.writelines('export PATH={}:$PATH\n'.format(paths["flexpart_src"]))
        fh.writelines('$(sed -n \"${{SLURM_ARRAY_TASK_ID}}p\" paths.txt)\n')
        fh.writelines('cd $DIR\n')
        fh.writelines("time FLEXPART\n")

        # fh.writelines('echo \"{} ,       COMPLETED \" >> {}/COMPLETED_RUNS \n'.format(folderName,
        #             paths["abs_path"]))
        fh.writelines('exit 0' )



def makefolderStruct(dateI,paths):
    """
    DESCRIPTION
    ===========

        Sets up FLEXPART folder structure and return path to the folder.

    USEAGE:
    =======

        folderName = makefolderStruct(dateI,paths)

        params:
            dateI pandas.dateTime object
            paths dictionary containing FLEXPART paths.

        return:
            path to FLEXPART folder 
    """
    folderName = paths["abs_path"] + '/' + dateI.strftime("%Y%m%d_%H")
    os.mkdir(folderName)
    os.mkdir(folderName + '/options')
    os.mkdir(folderName + '/output')
    os.mkdir(folderName +'/options/SPECIES')
    return folderName

def update_dict(d, u):
    """Update dictionary recusively"""
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def write_release_file(path, site_dict, release_dict 
                            ,dateI , release_duration):
    release_dict = release_dict.copy()

    with open(path, 'w') as outfile:
        outfile.writelines('&RELEASES_CTRL\n')
        outfile.writelines('NSPEC = {},\n'.format(len(site_dict)))
        outfile.writelines('SPECNUM_REL = {}*1\n'.format(len(site_dict)))
        outfile.writelines('/\n')
        rel_comment = release_dict.pop('COMMENT')
        for key, site in site_dict.items():
            
            temp_dict = release_dict
            temp_dict['LON1'] = site['lon']
            temp_dict['LON1'] = site['lon']
            temp_dict['LAT1'] = site['lat']
            temp_dict['LAT1'] = site['lat']
            temp_dict['IDATE1'] = (dateI+release_duration).strftime('%Y%m%d')
            temp_dict['ITIME1'] = (dateI+release_duration).strftime('%H%M%S')
            temp_dict['IDATE2'] = dateI.strftime('%Y%m%d')
            temp_dict['ITIME2'] = dateI.strftime('%H%M%S')
            outfile.writelines('&RELEASE\n')
            for option, setting in temp_dict.items():
                outfile.writelines(option + ' = ' + setting + ',\n')
            outfile.writelines('COMMENT = ' + '\"' + site['comment'] + ' '+ rel_comment + '\"\n')
            outfile.writelines('/\n')


def setup_flexpart(settings=None):
    __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
    try:
        with open(os.path.join(__location__ ,'params.json')) as default_params:
            params = json.load(default_params)
    except FileNotFoundError:
        print("params.json not available in src!")
        sys.exit()

    if settings:
        params = update_dict(params, settings)



    paths = params['Paths']
    createParentDir(paths)
    simulation_params = params['Simulation_params']
    command = params['Command_Params']
    outgrid = params['Outgrid_params']
    species_params = params['Species_Params'] 
    site_dict = params['Receptor_locations']
    release_dict = params['Release_params']
    job_pramas = params["Job_params"]
    

    with open(paths["abs_path"] + "/COMPLETED_RUNS", "w") as cr:
        cr.writelines("Path,            STATUS \n")
    s = pd.to_datetime(simulation_params['start_date']+' '+simulation_params["start_time"])
    e = pd.to_datetime(simulation_params["end_date"]+' '+simulation_params["end_time"])
    date_range = pd.date_range(start=s,
                           end=e, freq=simulation_params["time_step"])
    sim_lenght = pd.to_timedelta(simulation_params["lenght_of_simulation"])
    release_duration = pd.to_timedelta(simulation_params["release_intervall"])
    dir_list = []
    for date in date_range:
        command['IBDATE'] = (date+sim_lenght).strftime('%Y%m%d')
        command['IBTIME'] =  (date+sim_lenght).strftime('%H%M%S')
        command['IEDATE'] = date.strftime('%Y%m%d')
        command['IETIME'] = date.strftime('%H%M%S')

        folderName = makefolderStruct(date, paths)
        write_namelist({'COMMAND':command},folderName + '/options/COMMAND')
        write_namelist({'OUTGRID':outgrid}, folderName + '/options/COMMAND')
        write_namelist({'SPECIES_PARAMS': species_params}, folderName + '/options/SPECIES/SPECIES_001')
        write_pathnames(folderName,paths)
        write_release_file(folderName + '/options/RELEASES', site_dict, 
                                release_dict,date, release_duration)
        dir_list.append(folderName)

    with open(os.path.join(paths['abs_path'], 'paths.txt'), 'w') as outfile:
         for path in dir_list:
             outfile.writelines(path + '\n')
    write_sbatct_file(job_pramas, date_range, paths)
    return params



def createParentDir(paths):
    """create parent directory"""
    try:
        os.mkdir(paths["abs_path"])
    except FileExistsError:
        askConfirmation = input("""This folder already exists,
        do you want to delete it? (y/n)""")
        if askConfirmation.strip() == 'y':
            shutil.rmtree(paths["abs_path"])
            os.mkdir(paths["abs_path"])
        else:
            sys.exit()
    os.chdir(paths["abs_path"])


if __name__=="__main__":

    parser = ap.ArgumentParser()
    parser.add_argument('--test', help="Setup one simulation, for check if setting is correct without submiting", action="store_true")
    parser.add_argument('--testAndSubmit', '--ts', help ="Setup one simulation and submit job", action="store_true")
    parser.add_argument('path', help='Path json to file containting simulation settings', default='flexpart_setup.py')
    parser.add_argument('--absPath', '--ap', help='Absolute path to topdirectory where flexpart simulation will be created', default=None)
    parser.add_argument('--edate','--ed', help='date of last flexpart run', default=None)
    parser.add_argument('--bdate', '--bd', help='date of fist flexpart run', default=None)
    args = parser.parse_args()

    test = False
    test_and_submit = False

    if args.test:
        test = True
    elif args.testAndSubmit:
        test_and_submit = True
    path = args.path
    abs_path = args.absPath
    e_date = args.edate
    b_date = args.bdate

    with open(path) as config_file:
        settings = json.load(config_file)
    if b_date:
        settings['Simulation_params'].update({'start_date': b_date})
    if e_date:
        settings['Simulation_params'].update({'end_date': e_date})
    if abs_path:
        settings['Paths'].update({'path_to_forcing': abs_path})
    setup_flexpart(settings)

