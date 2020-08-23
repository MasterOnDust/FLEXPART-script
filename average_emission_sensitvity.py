from netCDF4 import Dataset
from DUST import read_multiple_flexpart_output
import time
import xarray as xr

import pandas as pd
from functools import partial

def not_usefull(ds):
    essentials = ['RELCOM','RELLNG1','RELLNG2','RELLAT1','RELLAT2','RELZZ1','RELZZ2',
                'RELKINDZ','RELSTART','RELEND','RELPART','RELXMASS','LAGE','ORO', 'spec001_mr']
    return  [v for v in ds.data_vars if v not in essentials]

def pre_sum(ds, pointspec):
    ds = ds.rename(dict(longitude = 'lon', time= 'btime', latitude='lat'))
    ds = ds.sel(pointspec=pointspec, numpoint=pointspec, numspec=pointspec, nageclass=0)
    ds = ds.assign_coords(time=pd.to_datetime(ds.iedate + ds.ietime))
    ds = ds.drop(not_usefull(ds))
    ds = ds.sum(dim='btime')


    return ds



def sum_emissions(path, ncfiles, pointspec ,date_slice=None, data_var='spec001_mr',**kwargs):
    pre = partial(pre_sum,pointspec=pointspec)


    if date_slice == None:
        dsets = xr.open_mfdataset(ncfiles, preprocess=pre, decode_times=False,
                            combine='nested', concat_dim='time', parallel=True)
        s_time = pd.to_datetime(dsets.time[0].values).strftime('%Y%m%d')
        e_time = pd.to_datetime(dsets.time[-1].values).strftime('%Y%m%d')

    else:
        s_time = pd.to_datetime(date_slice.start).strftime('%Y%m%d')
        e_time = pd.to_datetime(date_slice.stop).strftime('%Y%m%d')
        ncdict = {'{}'.format(pd.to_datetime(path[-17:-3])):path for path in ncfiles}
        ncdict = pd.DataFrame.from_dict(ncdict, orient='index')
        ncdict = ncdict[date_slice]
        dsets = xr.open_mfdataset(ncdict[0].values, preprocess=pre, decode_times=False,
                            combine='nested', concat_dim='time', parallel=True)


    
    outFileName = path + '/' + 'avg_gridtime_{}_{}'.format(e_time, s_time) + '.nc'
    d0 = xr.open_dataset(ncfiles[0], decode_times=False)
    d0 = d0.sel(pointspec=pointspec, numpoint=pointspec, numspec=pointspec)
    lats = d0.latitude.values
    lons = d0.longitude.values
    dims = d0.dims
    height = d0.height
    relpart = d0.RELPART.values
    relcom = str(d0.RELCOM.values)[2:].strip()[:-1].split()
    d0.close()
    ind_receptor = d0.ind_receptor
    
    if ind_receptor == 1:
        f_name = 'Conc_emsens'
        field_unit = 's'
        field_name = 'Sensitivity to Concentration'
    elif ind_receptor == 4:
        f_name = 'DryDep_emsens'
        field_unit = 'm'
        field_name = 'Sensitivity to dry deposition'
    elif ind_receptor == 3:
        f_name = 'WetDep_emsens'
        field_unit = 'm'
        field_name = 'Sensitivity to wet deposition'
    else:
        field = 'Spec_mr'
        field.units = 's'
        field_name = 'Unknown'

    try:
        ncfile = Dataset(outFileName, 'w', format="NETCDF4")
    except PermissionError:
        # If netcdf file exist delete old one
        os.remove(outFileName)
        ncfile = Dataset(outFileName, 'w', format='NETCDF4')
    
    ncfile.title = 'Flexpart emission sensitivity'
    ncfile.history = "Created " + time.ctime(time.time())
    # ncfile.flexpart_v = d0.source
    ncfile.receptor_name =  ' '.join(relcom)
    ncfile.reference = 'https://doi.org/10.5194/gmd-12-4955-2019'

    ncfile.avg_window_start = s_time
    ncfile.avg_window_end = e_time
    ncfile.particle_released = relpart

    lat_dim = ncfile.createDimension('lat', dims['latitude'])
    lon_dim = ncfile.createDimension('lon', dims['longitude'])
    height_dim = ncfile.createDimension('height', dims['height'])
    point_dim = ncfile.createDimension('npoint',1)

    lat = ncfile.createVariable('lat', 'f4', ('lat', ), **kwargs)
    lon = ncfile.createVariable('lon', 'f4', ('lon',), **kwargs)
    height = ncfile.createVariable('height', 'i4', ('height', ), **kwargs)

    rellat = ncfile.createVariable('RELLAT', 'f4', ('npoint',),**kwargs)
    rellat.units = 'degrees_north'
    rellat.long_name = 'latitude_receptor'

    rellon = ncfile.createVariable('RELLON', 'f4', ('npoint',), **kwargs)
    rellon.units = 'degrees_east'
    rellon.long_name = 'longitude_receptor'

    lon[:] = lons
    lat[:] = lats

    print(d0.RELLAT1.values)

    rellat[:] = d0.RELLAT1.values
    rellon[:] = d0.RELLNG1.values

    height[:] = d0.height.values


    field = ncfile.createVariable(f_name, 'f4', ('height','lat', 'lon'), **kwargs)
    field.units = field_unit
    field.long_name = field_name

    field[:] = dsets[data_var].mean(dim='time').values

    ncfile.close()

if __name__ == "__main__":
    import glob
    ncfiles = glob.glob('../FLEXPART_output/dry_dep/**/grid*.nc', recursive=True)
    ncfiles.sort()
    sum_emissions('../',ncfiles,0)