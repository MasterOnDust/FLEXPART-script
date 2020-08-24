import xarray as xr
from dask.distributed import LocalCluster, Client
import DUST
import argparse as ap
import pandas as pd

import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = ap.ArgumentParser(description='Plot timeseries of Concentration/Dry-/Wet deposition')
    parser.add_argument('path_2micron',  help='path to output 2micron')
    parser.add_argument('path_20micron',  help='path to output 20micron')
    parser.add_argument('--etime','--et', default=None, help='end date of timeseries plot')
    parser.add_argument('--stime', 'st', default=None, help='start data of timeseries plot')
    parser.add_argument('--seasonal','--s', action='store_true', help='''create seasonal time series 
                        disregard etime and stime''')
    parser.add_argument('--out_dir', '--op' ,help='path to where output should be stored', default='.')
    parser.add_argument('--use_cluster', '--uc',action='store_true')
    args = parser.parse_args()
    seasonal = args.seasonal
    e_time = args.etime
    s_time = args.stime
    path_2micron = args.path_2micron
    path_20micron = args.path_20micron
    outpath = args.out_dir
    use_cluster = args.use_cluster
    date_slices = []

    if use_cluster == True:
        cluster = LocalCluster(n_workers=32, threads_per_worker=1, memory_limit='16GB')
        client= Client(cluster)
        print(cluster)
        
    d0 = xr.open_dataset(path_2micron[0])
    loc_name = d0.receptor_name.split()[0]
    data_var = d0.srr.var
    d0.close()
    p_sizes = ['2micron $\mu m$', '20 $\mu m$']
    if seasonal == True:
        date_slices.append(slice('2019-03-01','2019-05-31'))
        date_slices.append(slice('2019-06-01', '2019-08-31'))
        date_slices.append(slice('2019-09-01','2019-10-31')) 
    
    else:
        if e_time == None:
            e_time = pd.to_datetime(d0.time[-1].values).strftime('%Y-%m-%d')
        if s_time == None:
            s_time = pd.to_datetime(d0.time[0].values).strftime('%Y-%m-%d')
        
        date_slices.append(slice(e_time,s_time))

    dsets = []
    for path in [path_2micron, path_20micron]:
        dset = xr.open_dataset(path)
        dset = dset.srr.make_time_seires()
        dset.to_netcdf(outpath +'/{}_{}_2019'.format(data_var, loc_name) + '.nc')
        dsets.append(dset.persist()) 

    for date_slice in date_slices:
        fig, (ax,ax1) = plt.subplots(2,1,sharex=True, sharey=True, figsize=(16,5))
        
        for dset, ax_i, color, p_size in zip(dsets,(ax,ax1),['saddlebrown', 'sandybrown'], p_sizes):
            temp_dset = dset.sel(time=date_slice)
            ax_i = temp_dset.srr.plot_time_series(ax=ax_i, label = dset.receptor_name + ' ' + p_size)
            ax_i.legend()
            ax_i.grid(linestyle='-')
        ax1.axes.xaxis.label.set_visible(False)
        plt.savefig(outpath+'/{}_{}_{}_{}'.format(data_var,loc_name, date_slice.start, date_slice.stop) + '.png'
                                , dpi=300, bbox_inches='tight')




