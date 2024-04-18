
# written by cwa   14/04/2024

# this script takes data that has already been processed to .csv and creates a .pkl file

# merge this into a utility file..

import pandas as pd

filename = 'NQH41S'
datapath = '/Users/cw/Library/CloudStorage/ProtonDrive-xxh_i@proton.me/data/curiousgeorge/processed/NQ_H4_1s.csv'

def txt_to_pickle(filename, datapath):
        data = pd.read_csv(datapath)
        data['DateTime'] = pd.to_datetime(data['DateTime'], format='%Y-%m-%d %H:%M:%S')
        data.to_pickle(filename + '.pkl')
        exit

txt_to_pickle(filename, datapath)
