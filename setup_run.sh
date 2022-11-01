set -o nounset 

psizes=('2micron' '20micron')
kind_list=('drydep' 'wetdep')
bds=('0311' '0401' '0501')
eds=('0331' '0430' '0531')

outpath='/cluster/work/users/ovewh/FLEXPART_updated_domain/'
rm -r ${outpath}
mkdir ${outpath}
for kind in "${kind_list[@]}";
do
    mkdir ${outpath}${kind} 
    for psize in "${psizes[@]}"; 
    do
        mkdir ${outpath}${kind}/${psize} 
        for year in {1999..2019};
            do
                # for i in {0..2}; 
                # do 
            
                    jobscript.py options/${psize}_${kind}.json --ap /cluster/work/users/ovewh/FLEXPART_updated_domain/${kind}/${psize}/${year}/ --pl \
                            --pf /cluster/projects/nn2806k/ovewh/AVAILABLE_WINDFIELDS_EA --bd ${year}${bds[0]} --ed ${year}${eds[2]}
                # done
            done 
      done
done
