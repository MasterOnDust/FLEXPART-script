from params import sites
import argparse as ap
import os
from simulation import *
import pandas as pd
import shutil
import sys

def write_species(folderName):
    settings = SPEC.species_Params
    with open(folderName +'/options/SPECIES/SPECIES_001', 'w') as sp:
        sp.writelines('&SPECIES_PARAMS\n')
        for option, setting in settings.items():
            sp.writelines(option + ' = ' + setting + ',\n')
        sp.writelines('/')

def write_command(folderName):
    settings =  COMMAND.command
    with open(folderName + '/options/COMMAND', 'w') as c:
        c.writelines('&COMMAND\n')
        for option, setting in settings.items():
            c.writelines(option + ' = ' + setting + ',\n')

        c.writelines('/')

def write_outgrid(folderName):
    settings = OUTGRID.outgrid
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
        pn.writelines(path_to_forcing + '\n')
        pn.writelines('============================================')

def write_release_file(sites, specNum, folderName):
    nspec = len(sites)
    rel_comment = RELEASES.comment
    with open(folderName+'/options/RELEASES', 'w') as r:
        r.writelines('&RELEASES_CTRL\n')
        r.writelines('NSPEC = {},\n'.format(nspec))
        r.writelines('SPECNUM_REL = {}*{},\n'.format(nspec, specNum))
        for site in sites:
            RELEASES.LON1 = site.lon
            RELEASES.LON2 = site.lon
            RELEASES.LAT1 = site.lat
            RELEASES.LAT2 = site.lat
            RELEASES.comment = '\"' + site.comment + rel_comment + '\"'
            write_single_release(r)

        r.writelines('/')

def write_single_release(outfile):
    outfile.writelines('/\n')
    settings = RELEASES.release

    outfile.writelines('&RELEASE\n')
    for option, setting in settings.items():
        outfile.writelines(option + ' = ' + setting + ',\n')




def submit_job(dateI, folderName):
#   Should make jobfile configurable from simulation.py
    str_date = dateI.strftime("%Y%m%d-%H")
    job_file = folderName + '/submit_' + dateI.strftime("%Y%m%d_%H") + '.sh'
    with open(job_file, 'w') as fh:
        fh.writelines("#!/bin/bash\n")
        fh.writelines("#SBATCH --account=nn2806k\n")
        fh.writelines("#SBATCH --job-name=FLEXPART_{}\n".format(str_date))
        fh.writelines("#SBATCH --time=1:00:00\n")
        fh.writelines("#SBATCH --ntasks=1\n")
        fh.writelines("#SBATCH --mem-per-cpu=6G\n")
       # fh.writelines("#SBATCH --error=.out_{}.err\n".format(folderName))
       # fh.writelines("#SBATCH --output=.out_{}.out\n".format(folderName))
        fh.writelines('set -o errexit\n')
        fh.writelines('set -o nounset\n')
        fh.writelines('module --quiet purge\n')

        fh.writelines('module load ecCodes/2.9.2-intel-2018b\n')
        fh.writelines('module load netCDF-Fortran/4.4.4-intel-2018b\n')
        fh.writelines('export PATH=/cluster/projects/nn2806k/flexpart/flexpart/src:$PATH\n')
        fh.writelines('cd {}\n'.format(folderName))
        fh.writelines("time FLEXPART\n")
        fh.writelines('exit 0' )
    os.system("sbatch %s" %job_file)

def makefolderStruct(dateI):
    folderName = abs_path + '/' + dateI.strftime("%Y%m%d_%H")
    os.mkdir(folderName)
    os.mkdir(folderName + '/options')
    os.mkdir(folderName + '/output')
    os.mkdir(folderName +'/options/SPECIES')
    for filename in os.listdir(flexpart_input_path):
        shutil.copy(flexpart_input_path + '/' + filename, folderName + '/options/')

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
    s = pd.to_datetime(start_date+' '+start_time)
    e = pd.to_datetime(end_date+' '+end_time)
    date_range = pd.date_range(start=s,
                           end=e, freq=time_step)
    sim_lenght = pd.to_timedelta(lenght_of_simulation)
    release_duration = pd.to_timedelta(release_intervall)

    for date in date_range:

        COMMAND.IBDATE = (date+sim_lenght).strftime('%Y%m%d')
        COMMAND.IBTIME = (date+sim_lenght).strftime('%H%M%S')
        COMMAND.IEDATE = date.strftime('%Y%m%d')
        COMMAND.IETIME = date.strftime('%H%M%S')

        RELEASES.IDATE1 = (date+release_duration).strftime('%Y%m%d')
        RELEASES.ITIME1 = (date+release_duration).strftime('%H%M%S')
        RELEASES.IDATE2 = date.strftime('%Y%m%d')
        RELEASES.ITIME2 = date.strftime('%H%M%S')
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
            continue



def createParentDir():
    try:
        os.mkdir(abs_path)
    except FileExistsError:
        askConfirmation = input("""This folder already exists,
        do you want to delete it? (y/n)""")
        if askConfirmation.strip() == 'y':
            shutil.rmtree(abs_path)
            os.mkdir(abs_path)
        else:
            sys.exit()
    os.chdir(abs_path)


if __name__=="__main__":
    parser = ap.ArgumentParser()
    parser.add_argument('--test', help="Setup one simulation, for check if setting is correct without submiting", action="store_true")
    parser.add_argument('--testAndSubmit', '--ts', help ="Setup one simulation and submit job", action="store_true")
    args = parser.parse_args()
    test = False
    test_and_submit = False
    if args.test:
        test = True
    elif args.testAndSubmit:
        test_and_submit = True
    site_dict = tracing_the_winds_sites()
    site_list = [site_dict[loc] for loc in locations]
    createParentDir()
    setup_flexpart(site_list)


