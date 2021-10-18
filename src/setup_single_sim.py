#!/usr/bin/env python
"""
Setup single FLEXPAT simulation

"""


from jobscript import setup_single_flexpart_simulation
import argparse as ap
import os
import pandas as pd
import json
from IPython import embed

if __name__=="__main__":

    parser = ap.ArgumentParser()
    parser.add_argument('path', help='Path json to file containting simulation settings')

    parser.add_argument('date',
                        help='date  fmt YYYY-MM-DD')
    parser.add_argument('time',help='end time of last simulation fmt HH:MM:SS')
    parser.add_argument('--release_intervall','--ri',default='3h')
    parser.add_argument('--path_to_forcing', '--pf', default=None,help='path to model forcing')
    parser.add_argument('--lenght_of_trajectory', '--lof',default='5d')
    parser.add_argument('--absPath', '--ap',
                        help='Absolute path to topdirectory where flexpart simulation will be created', default='./')
    parser.add_argument('--continuous_release', '--cr', action='store_true')
    args = parser.parse_args()
    path = args.path
    abs_path = args.absPath
    e_date = args.date
    path_to_forcing = args.path_to_forcing
    e_time=args.time
    lenght_of_trajectory = args.lenght_of_trajectory
    rel_int = args.release_intervall
    continuous_release = args.continuous_release


    with open(path) as config_file:
        settings = json.load(config_file)
    e_date = pd.to_datetime(e_date+' '+e_time)
    rel_int = pd.to_timedelta(rel_int)
    b_date = e_date - rel_int



    settings['Simulation_params'].update({'start_date': e_date.strftime('%Y-%m-%d')})
    settings['Simulation_params'].update({'end_date': e_date.strftime('%Y-%m-%d')})
    settings['Simulation_params'].update({'start_time': e_date.strftime('%H:%M:%S')})
    settings['Simulation_params'].update({'end_time': e_date.strftime('%H:%M:%S')})
    if path_to_forcing:
        settings['Paths'].update({'path_to_forcing': path_to_forcing})
    if abs_path:
        settings['Paths'].update({'abs_path':abs_path})
    if continuous_relese:
        t0 = pd.to_datetime('')

    setup_single_flexpart_simulation(settings)
