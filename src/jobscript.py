#!/usr/bin/env python
import argparse as ap
import os
import pandas as pd
import shutil
import sys
import f90nml
import json
import collections.abc

def write_to_file(params_dict,path, identifier):
    with open(path, 'w') as outfile:
        outfile.writelines('&{}\n'.format(identifier))
        for option, setting in params_dict.items():
            outfile.writelines(option + ' = ' + setting + ',\n')
        outfile.writelines('/')


def write_namelist(params_dict,path):
    nml = f90nml.Namelist(params_dict)
    nml.end_comma = True
    nml.uppercase = True
    nml.indent = ''
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



def write_sbatch_file(jobscript_params,date, paths, batch_number):
    """Write sbatch slurm script for submitting array job"""
    date0 = date.strftime("%Y%m%d")
    jobscript_params = jobscript_params.copy()
    n_simulations_per_task = jobscript_params.pop('n_simulations_per_task')
#     date1 = daterange.tolist()[-1].strftime("%Y%m%d")
    job_file = paths['abs_path'] + '/submit_flexpart{}.sh'.format(date0)
    with open(job_file, 'w') as fh:
        fh.writelines("#!/bin/bash\n")
        for option, setting in jobscript_params.items():
            fh.writelines("#SBATCH --{}={}\n".format(option,setting))
        fh.writelines("#SBATCH --job-name=FLEXPART_{}\n".format(date0))
        fh.writelines("#SBATCH --error={}/log/out_%a{}.err\n".format(paths['abs_path'],date0))
        fh.writelines("#SBATCH --output={}/log/out_%a_{}.out\n".format(paths['abs_path'],date0))
        fh.writelines("#SBATCH --mail-type=FAIL\n")
        fh.writelines('set -o errexit\n')
        fh.writelines('set -o nounset\n')
        fh.writelines('module --quiet purge\n')
        fh.writelines('module load ecCodes/2.9.2-intel-2018b\n')
        fh.writelines('module load netCDF-Fortran/4.4.4-intel-2018b\n')
        fh.writelines('export PATH={}:$PATH\n'.format(paths["flexpart_src"]))
        fh.writelines('for ((i=1;i<={};i++))\n'.format(n_simulations_per_task))
        fh.writelines('do\n')
        fh.writelines('     let \"linenumber=((${SLURM_ARRAY_TASK_ID}-1)*{}+i)\"\n'.format(simulations_per_task))
        fh.writelines('     INPATH=$(sed -n \"${linenumber}p\"' + ' {}/paths{}.txt)\n'.format(paths['abs_path'],batch_number))
        fh.writelines('     if [ "$INPATH" == \"==\" ]; then\n')
        fh.writelines('          echo \"End of file reached\"\n')
        fh.writelines('     else\n')
        fh.writelines('          cd $INPATH\n')
        fh.writelines('          FLEXPART\n')
        fh.writelines('          echo \"$INPATH,       COMPLETED \" >> {}/COMPLETED_RUNS \n'.format(
                    paths["abs_path"]))
        fh.writelines('     fi\n')
        fh.writelines('done\n')
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

def write_release_file(path, site_dict, release_dict
                            ,dateI , release_duration):
    release_dict = release_dict.copy()

    with open(path, 'w') as outfile:
        outfile.writelines('&RELEASES_CTRL\n')
        outfile.writelines('NSPEC = {},\n'.format(len(site_dict)))
        outfile.writelines('SPECNUM_REL = {}*1,\n'.format(len(site_dict)))
        outfile.writelines('/\n')
        rel_comment = release_dict.pop('COMMENT')
        for key, site in site_dict.items():

            temp_dict = release_dict
            temp_dict['LON1'] = site['lon']
            temp_dict['LON2'] = site['lon']
            temp_dict['LAT1'] = site['lat']
            temp_dict['LAT2'] = site['lat']
            temp_dict['IDATE1'] = (dateI+release_duration).strftime('%Y%m%d')
            temp_dict['ITIME1'] = (dateI+release_duration).strftime('%H%M%S')
            temp_dict['IDATE2'] = dateI.strftime('%Y%m%d')
            temp_dict['ITIME2'] = dateI.strftime('%H%M%S')
            outfile.writelines('&RELEASE\n')
            for option, setting in temp_dict.items():
                outfile.writelines(option + ' = ' + setting + ',\n')
            outfile.writelines('COMMENT = ' + '\"' + site['comment'] + ' '+ rel_comment + '\"\n')
            outfile.writelines('/\n')


def setup_flexpart(settings):
    __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
#     try:
#         with open(os.path.join(__location__ ,'params.json')) as default_params:
#             params = json.load(default_params)
#     except FileNotFoundError:
#         print("params.json not available in src!")
#         sys.exit()

#     if settings:
#         params = update_dict(params, settings)



    paths = settings['Paths']
    createParentDir(paths)
    simulation_params = settings['Simulation_params']
    command = settings['Command_Params']
    outgrid = settings['Outgrid_params']
    species_params = settings['Species_Params']
    site_dict = settings['Receptor_locations']
    release_dict = settings['Release_params']
    job_params = settings["Job_params"]

    species_params["PSPECIES"] = '\"' +species_params["PSPECIES"]+ '\"'

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
        write_to_file(command,folderName + '/options/COMMAND', 'COMMAND')
        write_to_file(outgrid, folderName + '/options/OUTGRID', 'OUTGRID')
        write_to_file(species_params, folderName + '/options/SPECIES/SPECIES_001','SPECIES_PARAMS')
        write_pathnames(folderName,paths)
        write_release_file(folderName + '/options/RELEASES', site_dict,
                                release_dict,date, release_duration)
        dir_list.append(folderName)
    batch_size = int(job_params['array'].split('-')[1]*int(job_params['n_simulations_per_task']))
    batches = [dir_list]
    if len(dir_list) >= batch_size:
        batches = [dir_list[x:x+100] for x in range(0, len(dir_list), batch_size)]



    for i, batch in enumerate(batches):

        path_file = os.path.join(paths['abs_path'], f'paths{i}.txt')
        n_jobs = write_path_file(batch,path_file)
        job_params['array'] = '1-{}'.format(round(n_jobs/int(job_params['n_simulations_per_task'])))
        write_sbatch_file(job_params,pd.to_datetime(batch[0].split('/')[-1], format="%Y%m%d_%H"), paths,i)

    return settings

def write_path_file(batch, file_path):
    n_jobs = 0
    with open(file_path, 'w') as outfile:
        for path in (batch):
            outfile.writelines(path + '\n')
            n_jobs = n_jobs+1
        outfile.writelines("==")
    return n_jobs



# def write_path_file(batch, file_path):
#     n_jobs = 0
#     with open(file_path, 'w') as outfile:
#         for path1, path2 in zip(batch[1::2],batch[::2]):
#             outfile.writelines(path1 + ', ' + path2 + '\n')
#             n_jobs=n_jobs+1
#         if len(batch) % 2!=0:
#             outfile.writelines(batch[-1])
#             n_jobs=n_jobs+1
#     return n_jobs

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
    os.mkdir('log')


if __name__=="__main__":

    parser = ap.ArgumentParser()
#     parser.add_argument('--test', help="Setup one simulation, for check if setting is correct without submiting", action="store_true")
#     parser.add_argument('--testAndSubmit', '--ts', help ="Setup one simulation and submit job", action="store_true")
    parser.add_argument('path', help='Path json to file containting simulation settings')
    parser.add_argument('--absPath', '--ap', help='Absolute path to topdirectory where flexpart simulation will be created', default=None)
    parser.add_argument('--edate','--ed', help='date of last flexpart run', default=None)
    parser.add_argument('--bdate', '--bd', help='date of fist flexpart run', default=None)
    args = parser.parse_args()

    test = False
    test_and_submit = False

#     if args.test:
#         test = True
#     elif args.testAndSubmit:
#         test_and_submit = True
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

