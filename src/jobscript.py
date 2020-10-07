#!/usr/bin/env python

from params import sites
import argparse as ap
import os
import pandas as pd
import shutil
import sys
import importlib.util

def write_species(folderName):
    settings = sim.SPEC.species_Params
    with open(folderName +'/options/SPECIES/SPECIES_001', 'w') as sp:
        sp.writelines('&SPECIES_PARAMS\n')
        for option, setting in settings.items():
            sp.writelines(option + ' = ' + setting + ',\n')
        sp.writelines('/')

def write_command(folderName):
    settings =  sim.COMMAND.command
    with open(folderName + '/options/COMMAND', 'w') as c:
        c.writelines('&COMMAND\n')
        for option, setting in settings.items():
            c.writelines(option + ' = ' + setting + ',\n')

        c.writelines('/')

def write_outgrid(folderName):
    settings = sim.OUTGRID.outgrid
    with open(folderName + '/options/OUTGRID', 'w') as o:
        o.writelines('&OUTGRID\n')
        for option, setting in settings.items():
            o.writelines(option + ' = ' + setting + ',\n')
        o.writelines('/')
def write_pathnames(folderName):
    with open(folderName + '/pathnames', 'w') as pn:
        pn.writelines('./options/\n')
        pn.writelines('./output/\n')
        pn.writelines('/\n')
        pn.writelines(sim.path_to_forcing + '\n')
        pn.writelines(sim.flexpart_input_path + '\n')
        pn.writelines('============================================')

def write_release_file(sites, specNum, folderName):
    nspec = len(sites)
    rel_comment = sim.RELEASES.comment
    with open(folderName+'/options/RELEASES', 'w') as r:
        r.writelines('&RELEASES_CTRL\n')
        r.writelines('NSPEC = {},\n'.format(nspec))
        r.writelines('SPECNUM_REL = {}*{},\n'.format(nspec, specNum))
        for site in sites:
            sim.RELEASES.LON1 = site.lon
            sim.RELEASES.LON2 = site.lon
            sim.RELEASES.LAT1 = site.lat
            sim.RELEASES.LAT2 = site.lat
            sim.RELEASES.comment = '\"' + site.comment + rel_comment + '\"'
            write_single_release(r)
            sim.RELEASES.comment = rel_comment
        r.writelines('/')

def write_single_release(outfile):
    outfile.writelines('/\n')
    settings = sim.RELEASES.release

    outfile.writelines('&RELEASE\n')
    for option, setting in settings.items():
        outfile.writelines(option + ' = ' + setting + ',\n')



def submit_job(dateI, folderName):
#   Should make jobfile configurable from simulation.py
    str_date = dateI.strftime("%Y%m%d-%H")
    job_file = folderName + '/submit_' + dateI.strftime("%Y%m%d_%H") + '.sh'
    settings = sim.JOBSCRIPT.job_params
    with open(job_file, 'w') as fh:
        fh.writelines("#!/bin/bash\n")
        for option, setting in settings.items():
            fh.writelines("#SBATCH --{}={}\n".format(option,setting))
        fh.writelines("#SBATCH --job-name=FLEXPART_{}\n".format(str_date))
        fh.writelines("#SBATCH --error={}/out_{}.err\n".format(folderName,str_date))
        fh.writelines("#SBATCH --output={}/out_{}.out\n".format(folderName,str_date))
        fh.writelines("#SBATCH --mail-type=FAIL\n")
        fh.writelines('set -o errexit\n')
        fh.writelines('set -o nounset\n')
        fh.writelines('module --quiet purge\n')

        fh.writelines('module load ecCodes/2.9.2-intel-2018b\n')
        fh.writelines('module load netCDF-Fortran/4.4.4-intel-2018b\n')
        fh.writelines('export PATH={}:$PATH\n'.format(sim.flexpart_src))
        fh.writelines('cd {}\n'.format(folderName))
        fh.writelines("time FLEXPART\n")

        fh.writelines('echo \"{} ,       COMPLETED \" >> {}/COMPLETED_RUNS \n'.format(folderName,sim.abs_path))
        fh.writelines('exit 0' )
#     os.system("sbatch %s" %job_file)

def makefolderStruct(dateI):
    folderName = sim.abs_path + '/' + dateI.strftime("%Y%m%d_%H")
    os.mkdir(folderName)
    os.mkdir(folderName + '/options')
    os.mkdir(folderName + '/output')
    os.mkdir(folderName +'/options/SPECIES')
    #for filename in os.listdir(sim.flexpart_input_path):
    #    shutil.copy(sim.flexpart_input_path + '/' + filename, folderName + '/options/')

    write_pathnames(folderName)

    return folderName

def tracing_the_winds_sites():
    site_dict = {'SACOL': sites(lon='104.137', lat='35.964', comment='SACOL '),
                'BADOE': sites(lon='111.170', lat = '39.003', comment='BADOE '),
                'YINCHUAN': sites(lon='106.101', lat='38.500', comment='YINCHUAN '),
                'LINGTAI': sites(lon ='107.789', lat='35.065', comment='LINGTAI '),
                'LUOCHUAN': sites(lon='109.424', lat = '35.710', comment='LUOCHUAN '),
                'SHAPOTOU': sites(lon='105.0475', lat='37.749', comment='SHAPOTOU '),
                'LANTIAN' : sites(lon ='109.256', lat='34.180', comment='LANTIAN ')}
    return site_dict

def setup_flexpart(site_list):
    with open(sim.abs_path + "/COMPLETED_RUNS", "w") as cr:
        cr.writelines("Path,            STATUS \n")
    s = pd.to_datetime(sim.start_date+' '+sim.start_time)
    e = pd.to_datetime(sim.end_date+' '+sim.end_time)
    date_range = pd.date_range(start=s,
                           end=e, freq=sim.time_step)
    sim_lenght = pd.to_timedelta(sim.lenght_of_simulation)
    release_duration = pd.to_timedelta(sim.release_intervall)

    for date in date_range:

        sim.COMMAND.IBDATE = (date+sim_lenght).strftime('%Y%m%d')
        sim.COMMAND.IBTIME = (date+sim_lenght).strftime('%H%M%S')
        sim.COMMAND.IEDATE = date.strftime('%Y%m%d')
        sim.COMMAND.IETIME = date.strftime('%H%M%S')

        sim.RELEASES.IDATE1 = (date+release_duration).strftime('%Y%m%d')
        sim.RELEASES.ITIME1 = (date+release_duration).strftime('%H%M%S')
        sim.RELEASES.IDATE2 = date.strftime('%Y%m%d')
        sim.RELEASES.ITIME2 = date.strftime('%H%M%S')
        folderName = makefolderStruct(date)
        write_command(folderName)
        write_outgrid(folderName)
        write_species(folderName)
        write_release_file(site_list, '1', folderName)
        if test:
            break
        elif test_and_submit:
            submit_job(date, folderName)
            break
        else:
            submit_job(date,folderName)



def createParentDir():
    try:
        os.mkdir(sim.abs_path)
    except FileExistsError:
        askConfirmation = input("""This folder already exists,
        do you want to delete it? (y/n)""")
        if askConfirmation.strip() == 'y':
            shutil.rmtree(sim.abs_path)
            os.mkdir(sim.abs_path)
        else:
            sys.exit()
    os.chdir(sim.abs_path)


if __name__=="__main__":

    parser = ap.ArgumentParser()
    parser.add_argument('--test', help="Setup one simulation, for check if setting is correct without submiting", action="store_true")
    parser.add_argument('--testAndSubmit', '--ts', help ="Setup one simulation and submit job", action="store_true")
    parser.add_argument('path', help='Path to file containting simulation settings', default='flexpart_setup.py')
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
    arg_path = args.absPath
    e_date = args.edate
    b_date = args.bdate
    spec = importlib.util.spec_from_file_location('*', path)
    sim = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim)

    if b_date:
        sim.start_date = b_date
    if e_date:
        sim.end_date = e_date

    if arg_path:
        sim.abs_path = arg_path

    sim.abs_path = os.path.abspath(sim.abs_path)

    site_dict = tracing_the_winds_sites()
    if sim.locations == 'ALL':
        site_list = [site_dict[loc] for loc in site_dict.keys()]
    else:
        site_list = [site_dict[loc] for loc in sim.locations]
    createParentDir()
    setup_flexpart(site_list)


