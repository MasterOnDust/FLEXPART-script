import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
from DUST.utils.maps import map_terrain_china
from DUST.utils.plotting import mpl_base_map_plot_xr
import argparse as ap
import os
import glob

def plot_map_emission_sensitivity(path_2micron, path_20micron, location,
                                    height=100, outpath='.'):

    p_sizes = ['2 $\mu m$', '20 $\mu m$']
    fig, (ax, ax1) = plt.subplots(2,1,subplot_kw={'projection':ccrs.PlateCarree()}, figsize= (18,8))

    if height == 100:
        title_str = 'surface'
    else:
        title_str = height

    for path, p_size, ax_i in zip([path_2micron,path_20micron], p_sizes, (ax,ax1)):
        dset = xr.open_dataset(path)
        if 'Conc_emsens' in dset.data_vars:
            dset = dset.assign_attrs({'varName': 'Conc_emsens'})
        elif 'DryDep_emsens' in dset.data_vars:
            dset = dset.assign_attrs({'varName': 'DryDep_emsens'})
        elif 'WetDep_emsens' in dset.data_vars:
            dset = dset.assign_attrs({'varName': 'WetDep_emsens'})
        else:
            raise(IndexError('unknown datavar in dataset {}'.format(dset.data_vars)))
        
        ax_i = map_terrain_china(ax_i)
        ax_i = mpl_base_map_plot_xr(dset,ax_i,vmin=1e-2,mark_receptor=True,)
        ax_i.text(0.2,0.1, p_size,transform =ax.transAxes, horizontalalignment='center', verticalalignment='center',
                bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 5}, fontsize=16)
        
    ax.set_title('Averaged {} emission sensitivity {}-{}'.format(title_str,dset.avg_window_start,
                                            dset.avg_window_end))
    ax1.axes.title.set_visible(False)
    plt.savefig('{}_{}_{}m_{}_{}.png'.format(dset.varName,location,height,
                    dset.avg_window_start, dset.avg_window_end), dpi=300, bbox_inches='tight')

    plt.close()

if __name__ == "__main__":
    parser = ap.ArgumentParser(description='Plot averaged maps of emission sensitivity')
    parser.add_argument('path_2micron',  help='path to output 2micron')
    parser.add_argument('path_20micron',  help='path to output 20micron')
    parser.add_argument('--out_dir', '--op' ,help='path to where output should be stored', default='./out')
    parser.add_argument('--height', '--h', help='Which OUTGRID layer to plot', default=100)
    args = parser.parse_args()

    path_2micron = args.path_2micron
    path_20micron = args.path_20micron
    outpath = args.out_dir
    height = args.height
    files_2m = glob.glob(path_2micron +'**.nc', recursive=True)
    files_20m = glob.glob(path_20micron + '**.nc', recursive=True)

    os.mkdir(outpath)

    path_dict_2m = {f_name.split('_')[0] : f_name for f_name in files_2m}
    path_dict_20m = {f_name.split('_')[0] : f_name for f_name in files_20m}
    for key, item in path_dict_2m.items():
        plot_map_emission_sensitivity(item, path_20micron[key],location=key, height=height, outpath=outpath)
