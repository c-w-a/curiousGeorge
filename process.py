
# written by cwa 26/02/2024

# this script processes data exported from Sierra Chart so that its datetimes have the same precision and format as the rest of the system

# merge this into a utility file..

import pandas as pd

filepath = '/Users/cw/Library/CloudStorage/ProtonDrive-xxh_i@proton.me/data/curiousgeorge/historicaldata/NQ/NQH4.CME.txt'
filename = 'NQ_H4'

# FUNCTION : enforces microsecond time precision
def uniform_time_format(time):
    if '.' in time:
        return time + '000'
    else:
        return time + '.000000'

# read in raw data, remove spaces, keep times as strings
data = pd.read_csv(filepath, delimiter=', ', engine='python', converters={'Time': str})

# convert to binary bid/ask column
data['BidOrAsk'] = (data['BidVolume'] < data['AskVolume']).astype(int)

data['Time'] = data['Time'].apply(uniform_time_format)
data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
data.set_index('DateTime', inplace=True)

# resample data to 1-second intervals
ohlc = data['Last'].resample('1S').ohlc()
volume = data['Volume'].resample('1S').sum()
trade_count = data['NumberOfTrades'].resample('1S').sum()
data_1s = pd.concat([ohlc, volume, trade_count], axis=1)

data_1s.reset_index(inplace=True)

data_1s.to_csv('~/Downloads/' + filename + '_1s.csv')