#!/usr/bin/env python
"""
Setup single FLEXPAT simulation

"""


from jobscript import setup_single_flexpart_simulation
import argparse as ap
import os
import pandas as pd
import json

if __name__=="__main__":

    parser = ap.ArgumentParser()
    parser.add_argument('path', help='Path json to file containting simulation settings')

    parser.add_argument('date',
                        help='last of simlation date  fmt YYYY-MM-DD')
    parser.add_argument('time',help='end time of last simulation fmt HH:MM:SS')
    parser.add_argument('--release_interval','--ri',default='3h',
                    help='Specify release interval, in continuos release setup this should be set equal to LOUTSTEP')
    parser.add_argument('--path_to_forcing', '--pf', default=None,help='path to model forcing')
    parser.add_argument('--length_of_trajectory', '--lot',default=None,
                help='In single release simulations it determines the length of the simulation, For continuous simulations it determines the maximum age of the particles')
    parser.add_argument('--absPath', '--ap',
                        help='Absolute path to topdirectory where flexpart simulation will be created', default='./')
    parser.add_argument('--continuous_release', '--cr', action='store_true')
    parser.add_argument('--bdate', '--bd', help='Starting date of continuos release simulation fmt YYYY-MM-DD HH:MM:SS (not used except in continuos release setup)', default=None)

    parser.add_argument('--z1', help='lower bound release height', default=None)
    parser.add_argument('--z2', help='upper bound release height')
    parser.add_argument('--npart_rel', '--npr', help='Number of particles to release per lout_step (only used in continuos release setup)',
                        default=2000)
    args = parser.parse_args()
    path = args.path
    abs_path = args.absPath
    e_date = args.date
    path_to_forcing = args.path_to_forcing
    e_time=args.time
    length_of_trajectory = args.length_of_trajectory
    rel_int = args.release_interval
    continuous_release = args.continuous_release
    b_date = args.bdate
    npart_rel = args.npart_rel
    z1 = args.z1
    z2 = args.z2
    with open(path) as config_file:
        settings = json.load(config_file)
    e_date = pd.to_datetime(e_date+' '+e_time)
    rel_int = pd.to_timedelta(rel_int)
    if continuous_release:
        if b_date:
            try:
                s_time = pd.to_datetime(b_date)
            except:
                raise ValueError('Invalid date format')
            if s_time > e_date:
                raise ValueError('btime has to be less than date')

        else:
            start_date = settings['Simulation_params']['stat_date']
            start_time = settings['Simulation_params']['start_time']
            s_time = pd.to_datetime(f'{start_date} {start_time}')
            if s_time > e_date:
                raise ValueError('btime has to be less than etime, please update the .json file or explicitly specify --btime')
        settings['Simulation_params'].update({'start_date': s_time.strftime('%Y-%m-%d')})
        settings['Simulation_params'].update({'end_date': e_date.strftime('%Y-%m-%d')})
        settings['Simulation_params'].update({'start_time': s_time.strftime('%H:%M:%S')})
        settings['Simulation_params'].update({'end_time': e_date.strftime('%H:%M:%S')})
    else:
        b_date = e_date - rel_int
        settings['Simulation_params'].update({'start_date': e_date.strftime('%Y-%m-%d')})
        settings['Simulation_params'].update({'end_date': e_date.strftime('%Y-%m-%d')})
        settings['Simulation_params'].update({'start_time': e_date.strftime('%H:%M:%S')})
        settings['Simulation_params'].update({'end_time': e_date.strftime('%H:%M:%S')})
    if z2:
        settings['Release_params'].update({'Z2':str(z2)})

    if z1:
        z2 = settings['Release_params']['Z2']
        if int(z2) < int(z1):
            raise ValueError('z1 cannot be smaller than z0')
        settings['Release_params'].update({'Z1':str(z1)})
    if path_to_forcing:
        settings['Paths'].update({'path_to_forcing': path_to_forcing})
    if abs_path:
        settings['Paths'].update({'abs_path':abs_path})
    if continuous_release:
        npart_rel = int(npart_rel)

        nparts = round(((e_date - s_time).days *npart_rel * 24)/(int(rel_int.seconds/(60*60))))

        settings['Release_params'].update({'PARTS':str(nparts)})

        if length_of_trajectory:
            try:
                dt = pd.to_timedelta(length_of_trajectory)
            except ValueError:
                print(f'Invalid time delta provided {length_of_trajectory}')

            settings['Ageclass_params'].update({'LAGE':'{}'.format(int(dt.total_seconds()))})
        t0 = pd.to_datetime('')
    else:
        settings['Command_Params'].update({'LAGESPECTRA':'0'})

    setup_single_flexpart_simulation(settings, continuous_release)
