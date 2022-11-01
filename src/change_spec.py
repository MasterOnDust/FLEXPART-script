#!/usr/bin/env python
import json
import argparse as ap

if __name__ == "__main__":
    parser = ap.ArgumentParser(description='Copy and change paramters in the FLEXPART backward simulation specification')
    parser.add_argument('reference_file',help='path to reference files')
    parser.add_argument('spec_name', help='name of new spec parameter')
    parser.add_argument('outpath', help='outpath for the new jobscript setup file')
    parser.add_argument('--dsigma','--s', help='new sigma', default=None)
    parser.add_argument('--pdquer', '--dq', help='new mean particle diameter', default=None)
    # parser.add_argument('')

    args = parser.parse_args()

    infile = args.reference_file
    pdquer = float(args.pdquer)
    spec_name = args.spec_name
    dsigma = float(args.dsigma)
    outfile = args.outpath

    infile= "/cluster/home/ovewh/FLEXPART-script/options/ref.json"
    
    with open(infile, 'r') as f:
        params = json.load(f)
        params = params.copy()
    params['Release_params']['COMMENT'] = spec_name
    params['Species_Params']['PSPECIES'] = spec_name 
    if pdquer:
        params['Species_Params']['PDQUER'] = f'{pdquer :2.2E}'
    if dsigma:
        params['Species_Params']['PDSIGMA'] = f'{dsigma :2.2E}'
    

    with open(outfile, 'w') as of:
        json.dump(params,of,indent=2)
    
    
    


    