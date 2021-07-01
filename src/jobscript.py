#!/usr/bin/env python
"""
Setup multiple FLEXPART simulation, to be submitted
to queue on saga.

"""
import argparse as ap
from datetime import date
import os
import pandas as pd
import shutil
import sys

from pandas.core.indexes.datetimes import date_range
import f90nml
import json
import collections.abc
from IPython import embed

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

def write_sbatch_file_per_site(jobscript_params,date, location,folderName,paths):
    date0 = date.strftime("%Y%m%d")
    filter_keys = ['account', 'time', 'ntasks', 'mem-per-cpu', 'mail-user']
    jobscript_params = {param: jobscript_params[param] for param in filter_keys}
    job_file = folderName + '/job_{}_{}.sh'.format(location, date0)
    with open(job_file, 'w') as fh:
        fh.writelines("#!/bin/bash\n")
        for option, setting in jobscript_params.items():
            fh.writelines("#SBATCH --{}={}\n".format(option,setting))
        fh.writelines("#SBATCH --job-name=FLEXPART_{}_{}\n".format(date0, location))
        fh.writelines("#SBATCH --error={}/log/out_{}_{}.err\n".format(paths['abs_path'],date0,location))
        fh.writelines("#SBATCH --output={}/log/out_{}_{}.out\n".format(paths['abs_path'],date0,location))
        fh.writelines("#SBATCH --mail-type=FAIL\n")
        fh.writelines('set -o errexit\n')
        fh.writelines('set -o nounset\n')
        fh.writelines('module --quiet purge\n')

        fh.writelines('module load ecCodes/2.9.2-intel-2018b\n')
        fh.writelines('module load netCDF-Fortran/4.4.4-intel-2018b\n')
        fh.writelines('export PATH={}:$PATH\n'.format(paths["flexpart_src"]))
        fh.writelines('cd {}\n'.format(folderName))
        fh.writelines("time FLEXPART\n")

        fh.writelines('echo \"{} ,       COMPLETED \" >> {}/COMPLETED_RUNS \n'.format(folderName,
                    paths["abs_path"]))
        fh.writelines('exit 0' )



def write_sbatch_file_release_time_step_array(jobscript_params,date, paths, batch_number):
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


def write_sbatch_file_release_time_step(jobscript_params,date, paths):
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

        fh.writelines('          echo \"$INPATH,       COMPLETED \" >> {}/COMPLETED_RUNS \n'.format(
                    paths["abs_path"]))
        fh.writelines('done\n')
        fh.writelines('exit 0' )

def makefolderStruct(dateI,paths, site_name=None):
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
    if site_name:
        folderName = paths["abs_path"] + '/' + dateI.strftime("%Y%m%d_%H") + site_name
    else:
        folderName = paths["abs_path"] + '/' + dateI.strftime("%Y%m%d_%H")
    os.mkdir(folderName)
    os.mkdir(folderName + '/options')
    os.mkdir(folderName + '/output')
    os.mkdir(folderName +'/options/SPECIES')
    return folderName

def write_release_file_time_step(path, site_dict, release_dict
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


def write_release_file_per_site(path, site, release_dict, sdate, edate, time_step, release_duration='3h'):
    """
    Create RELEASE file with a new relese every time_step.
    Simulate longer periods of one location

    """
    release_dict = release_dict.copy()
    dateRange = pd.date_range(start=sdate.strftime('%Y-%m-%d'), end=edate.strftime('%Y-%m-%d'), freq=time_step)
    rel_comment = release_dict.pop('COMMENT')
    with open(path, 'w') as outfile:
        outfile.writelines('&RELEASES_CTRL\n')
        outfile.writelines('NSPEC = 1,\n')
        outfile.writelines('SPECNUM_REL = 1,\n')
        outfile.writelines('/\n')
        for date in dateRange:
            temp_dict = release_dict
            temp_dict['LON1'] = site['lon']
            temp_dict['LON2'] = site['lon']
            temp_dict['LAT1'] = site['lat']
            temp_dict['LAT2'] = site['lat']
            temp_dict['IDATE1'] = (date+release_duration).strftime('%Y%m%d')
            temp_dict['ITIME1'] = (date+release_duration).strftime('%H%M%S')
            temp_dict['IDATE2'] = date.strftime('%Y%m%d')
            temp_dict['ITIME2'] = date.strftime('%H%M%S')
            outfile.writelines('&RELEASE\n')
            for option, setting in temp_dict.items():
                outfile.writelines(option + ' = ' + setting + ',\n')
            outfile.writelines('COMMENT = ' + '\"' + date.strftime('%Y%m%d%H') + ' ' + site['comment'] + ' '+ rel_comment + '\"\n')
            outfile.writelines('/\n')
def write_ageclass(path,max_age):
    """
    Write AGECLASS file to options folder

    """

    lage_max = abs(pd.to_timedelta(max_age).total_seconds())
    with open(path, 'w') as outfile:
        outfile.writelines('&AGECLASS\n')
        outfile.writelines('  NAGECLASS= 1,\n')
        outfile.writelines('  LAGE= {}\n'.format(int(lage_max)))
        outfile.writelines('/')

def setup_flexpart_per_site(settings, freq='M'):
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
    s = pd.to_datetime(simulation_params['start_date']+' '+simulation_params["start_time"])
    e = pd.to_datetime(simulation_params["end_date"]+' '+simulation_params["end_time"])
    date_range = pd.date_range(start=s,
                           end=e, freq=freq)
    date_list = date_range.to_list()
    date_list.insert(0,s)
    date_list[-1] = e

    with open(paths["abs_path"] + "/COMPLETED_RUNS", "w") as cr:
        cr.writelines("Path,            STATUS \n")

    sim_lenght = pd.to_timedelta(simulation_params["lenght_of_simulation"])
    release_duration = pd.to_timedelta(simulation_params["release_intervall"])
    dir_list = []

    command['LAGESPECTRA'] = '1'
    for site, site_params in site_dict.items():
        for i in range(1,len(date_list)):
            command['IBDATE'] = (date_list[i-1]+sim_lenght).strftime('%Y%m%d')
            command['IBTIME'] =  (date_list[i-1]+sim_lenght).strftime('%H%M%S')
            command['IEDATE'] = date_list[i].strftime('%Y%m%d')
            command['IETIME'] = date_list[i].strftime('%H%M%S')
            folderName = makefolderStruct(date_list[i], paths, site)
            write_ageclass(folderName +'/options/AGECLASSES', sim_lenght)
            write_to_file(command,folderName + '/options/COMMAND', 'COMMAND')
            write_to_file(outgrid, folderName + '/options/OUTGRID', 'OUTGRID')
            write_to_file(species_params, folderName + '/options/SPECIES/SPECIES_001','SPECIES_PARAMS')
            write_pathnames(folderName,paths)
            write_release_file_per_site(folderName + '/options/RELEASES', site_params,
                                    release_dict,date_list[i-1], date_list[i], simulation_params['time_step'],release_duration)
            dir_list.append(folderName)
            #(jobscript_params,date, location,folder_name,paths)
            write_sbatch_file_per_site(job_params, date_list[i], site, folderName, paths)

def setup_single_flexpart_simulation(settings):

    paths = settings['Paths']
    simulation_params = settings['Simulation_params']
    command = settings['Command_Params']
    outgrid = settings['Outgrid_params']
    species_params = settings['Species_Params']
    site_dict = settings['Receptor_locations']
    release_dict = settings['Release_params']
    job_params = settings["Job_params"]

    sim_lenght = pd.to_timedelta(simulation_params["lenght_of_simulation"])
    release_duration = pd.to_timedelta(simulation_params["release_intervall"])
    s = pd.to_datetime(simulation_params['start_date']+' '+simulation_params["start_time"])
    e = pd.to_datetime(simulation_params["end_date"]+' '+simulation_params["end_time"])

    command['IBDATE'] = (s+sim_lenght).strftime('%Y%m%d')
    command['IBTIME'] =  (s+sim_lenght).strftime('%H%M%S')
    command['IEDATE'] = s.strftime('%Y%m%d')
    command['IETIME'] = s.strftime('%H%M%S')
    command['LAGESPECTRA'] = '0'
    try:
        os.mkdir(paths["abs_path"])
    except FileExistsError:
        os.chdir(paths["abs_path"])


    folderName = paths["abs_path"] + '/' + s.strftime("%Y%m%d_%H")
    os.mkdir(folderName)
    os.mkdir(folderName + '/options')
    os.mkdir(folderName + '/output')
    os.mkdir(folderName +'/options/SPECIES')
    write_to_file(command,folderName + '/options/COMMAND', 'COMMAND')
    write_to_file(outgrid, folderName + '/options/OUTGRID', 'OUTGRID')
    write_to_file(species_params, folderName + '/options/SPECIES/SPECIES_001','SPECIES_PARAMS')
    write_pathnames(folderName,paths)
    write_release_file_time_step(folderName + '/options/RELEASES', site_dict,
                                release_dict,s, release_duration)

    date0=s.strftime('%Y%m%d_%H')
    job_file = folderName + '/submit_flexpart{}.sh'.format(date0)
    with open(job_file, 'w') as fh:
        fh.writelines("#!/bin/bash\n")
        fh.writelines("#SBATCH --job-name=FLEXPART_{}\n".format(date0))
        fh.writelines("#SBATCH --error={}/{}.err\n".format(folderName,date0))
        fh.writelines("#SBATCH --output={}/{}.out\n".format(folderName,date0))
        fh.writelines("#SBATCH --mail-type=FAIL\n")
        fh.writelines("#SBATCH --time={}\n".format(job_params['time']))
        fh.writelines("#SBATCH --mem-per-cpu={}\n".format(job_params['mem-per-cpu']))
        fh.writelines("#SBATCH --mail-user={}\n".format(job_params['mail-user']))
        fh.writelines("#SBATCH --account={}\n".format(job_params['account']))
        fh.writelines("#SBATCH --ntasks=1\n")
        fh.writelines('set -o errexit\n')
        fh.writelines('set -o nounset\n')
        fh.writelines('module --quiet purge\n')
        fh.writelines('module load ecCodes/2.9.2-intel-2018b\n')
        fh.writelines('module load netCDF-Fortran/4.4.4-intel-2018b\n')
        fh.writelines('export PATH={}:$PATH\n'.format(paths["flexpart_src"]))

        fh.writelines('cd {}\n'.format(folderName))
        fh.writelines('time FLEXPART\n')
        fh.writelines('exit 0' )

def setup_flexpart_per_time_step(settings):

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
        write_release_file_time_step(folderName + '/options/RELEASES', site_dict,
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
        write_sbatch_file_release_time_step(job_params,pd.to_datetime(batch[0].split('/')[-1], format="%Y%m%d_%H"), paths,i)

    return settings

def write_path_file(batch, file_path):
    n_jobs = 0
    with open(file_path, 'w') as outfile:
        for path in (batch):
            outfile.writelines(path + '\n')
            n_jobs = n_jobs+1
        outfile.writelines("==")
    return n_jobs


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

    parser = ap.ArgumentParser(description='''
            Python script for setting up flexpart backward simulations 
            based on model settings specified in a json file. Can either 
            setup the simulations in a per time step config or per location 
            config.  
    ''')
    parser.add_argument('path', help='Path json to file containting simulation settings')
    parser.add_argument('--absPath', '--ap', help='Absolute path to topdirectory where flexpart simulation will be created', default=None)
    parser.add_argument('--edate','--ed', help='date of last flexpart run', default=None)
    parser.add_argument('--path_to_forcing', '--pf', default=None,help='path file containing AVAILABLE textfile with path to forcing for each time step')
    parser.add_argument('--bdate', '--bd', help='date of fist flexpart run', default=None)
    parser.add_argument('--per_location', '--pl', action='store_true',
                    help='setup a flexpart simulation for each location')
    args = parser.parse_args()
    path = args.path
    abs_path = args.absPath
    e_date = args.edate
    b_date = args.bdate
    path_to_forcing = args.path_to_forcing
    per_location = args.per_location

    with open(path) as config_file:
        settings = json.load(config_file)
    if b_date:
        settings['Simulation_params'].update({'start_date': b_date})
    if e_date:
        settings['Simulation_params'].update({'end_date': e_date})
    if path_to_forcing:
        settings['Paths'].update({'path_to_forcing': path_to_forcing})
    if abs_path:
        settings['Paths'].update({'abs_path':abs_path})
    if per_location:
        setup_flexpart_per_site(settings)
    else:
        setup_flexpart_per_time_step(settings)

