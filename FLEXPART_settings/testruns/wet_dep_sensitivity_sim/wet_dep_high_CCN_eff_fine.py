from params import *

"""
DESCRIPTION
===========
    Define flexpart simulation settings.

AUTHOR
======
    Ove Haugvaldstad

"""

#Path to parent directory where the output of the simulation is stored
#abs_path = '/cluster/projects/nn2806k/ovewh/flexpart/RUNFLEXPART/Test'
abs_path = '/cluster/work/users/ovewh/wet_deposition_sensitivity_sims/Fine_silt_high_CCN_eff'

#Path to where the forcing AVAILABLE file is
path_to_forcing='/cluster/work/users/ovewh/AVAILABLE_WINDFIELDS'

#Path to where the landuse and surface data is stored
flexpart_input_path = '/cluster/projects/nn2806k/ovewh/flexpart/FLEXPART-script/FLEXPART_input'

#Path to flexpart src

flexpart_src = '/cluster/projects/nn2806k/ovewh/flexpart/flexpart/src'

#Parameters in jobscript submited to the jobqueue

JOBSCRIPT = Job_params(
    time = '00:40:00',
    mem_per_cpu = '8G'
)
#Time of first simulation
start_date = '2019-03-06'
start_time = '00:00:00'

#Time of last simulation
end_date = '2019-05-31'
end_time = '00:00:00'

# The time intervall between each simulation
time_step = '10800s'

# Duration of simulation, Remember backward simulation start and the end!
lenght_of_simulation = '-5d'

# Release Intervall
release_intervall = '-10800s' # has to be negative for backwards

# Which locations to simulate , if location is set to 'ALL', then all locations is used
locations = ('SACOL', 'BADOE', 'LANTIAN' )

#Settings in Command file, name of settings is the same as in the reference file
COMMAND = Command(
LDIRECT = '-1',
IOUT = '9', # NetCDF output 9 + 4 gives both central plume trajectories and emission sensitvities
IND_SOURCE = '1', # 1 Mass, corresponds to mass units 2, mixing ratio
IND_RECEPTOR = '3', # 3 Wet Deposition, 4 Dry depostion

LOUTSTEP= '10800',
LOUTAVER= '10800',
LCONVECTION = '1',
IOUTPUTFOREACHRELEASE= '1' # 1 -> seperate output for each release in the release file, HAS TO BE 1 in bw runs

)
#Set parameters for outgrid
OUTGRID = Outgrid()
#Parameters for flexpart particles, SPEC001_mr ile
SPEC = Species_Params(
    # Dry depositon parameter
    PSPECIES = 'FINE-SILT',
    PDQUER = '2.0E-06', # Particle size, mean diameter
    PDENSITY  =  '1400.000', # Density of the aerosol, negative -> no dry depostion
    PDSIGMA  = '1.250', # Measure of variation

    # In cloud scavaenging parameter
    PCCN_AERO = '0.4500000', #Cloud Condensation nuclei efficency (suggested value 0.9)
    PIN_AERO  = '0.1000000', #Ice Nuclei efficency, (suggested value 0.1)

)

RELEASES = Releases(COMMENT = 'FINE-SILT',
                    PARTS='200000')

