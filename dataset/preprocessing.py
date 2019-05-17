import pandas as pd

DATASET = '08_2018_bus.dsv'
CROPPED_DATASET = '07_08_2018_bus.dsv'
FINAL_DATASET = 'buses.dsv'
STOP_ID_MAPPING = {'bkz': 2583, 'liteyny_1': 20102, 'liteyny_1_2': 1660, # is for 3
                   'liteyny_0': 2864, 'liteyny_2': 4217, 'mayakovskogo': 3727, # 3461 mayakovskogo for 15, mistake
                   'railway_0': 2891, 'railway_1': 1691, 'suvorov_0': 3308, 'suvorov_1': 2119, 'vosst_0': 3278,
                   'vosst_1': 2090, 'zhukovskogo_22': 4954, 'zhukovskovgo_15': 4218, 'poltav_0': 2992, 'poltav_1': 1806}
AMBIGOUS_ROUTES_A = {'22': [2583, 2090, 20102], '24': [1806, 2119, 2090, 20102], '3': [1691, 2090, 1660],
                     '65': [1806, 2119, 2891], '181': [2090, 20102], '105': [2583, 2891], '74': [2583, 2891],
                     '27': [1806, 2119, 2090, 20102], '191': [1806, 2119, 2090, 20102]}
DURTY_DATA_BUSES = [7379, 1303, 6237, 6250, 1139, 1187, 6945, 6939]
DIRTY_ROUTES = ''


def cut_by_time(df, from_='2018-08-07 15:00', to='2018-08-07 17:00'):
    print(df.index.min(), df.index.max())
    df = df[from_:to]
    return df

def cut_unneeded_stops_and_buses(df):
    df = df[df['ID_STOP'].isin(STOP_ID_MAPPING.values())]
    df = df[~(df['ROUTE_NUMBER'] == 7)]
    df = df[~df['CARRIER_BOARD_NUM'].isin(DURTY_DATA_BUSES)]
    return df

def rename_stops(df):
    keys = list(STOP_ID_MAPPING.keys())
    values = list(STOP_ID_MAPPING.values())
    df['ID_STOP'] = df['ID_STOP'].apply(lambda x: keys[values.index(x)])
    df['ID_STOP'] = df['ID_STOP'].apply(lambda x: x if x != 'liteyny_1_2' else 'liteyny_1')
    return df

def disambiguate_route(row):
    old_route = str(row['ROUTE_NUMBER'])

    if old_route in AMBIGOUS_ROUTES_A.keys():
        if row['ID_STOP'] in AMBIGOUS_ROUTES_A[old_route]:
            new_route = f'{old_route}_a'
        else:
            new_route = f'{old_route}_b'
        # print(f'{old_route} -> {new_route}')
        row['ROUTE_NUMBER'] = new_route
    return row

def add_offset(df):
    offset = (df.index - df.index.min()).total_seconds() + 35
    df['OFFSET'] = offset.astype(int)
    return df

def group_routes(df):
    # reset index so that it wont go away when grouping
    df = df.reset_index()
    # order by 'CARRIER_NAME', 'CARRIER_BOARD_NUM'
    df = df.sort_values(['CARRIER_NAME', 'CARRIER_BOARD_NUM', 'STOP_TIME_REAL'])
    # print(df.head(15))
    # compute changed
    changed = df['ROUTE_NUMBER'].ne(df['ROUTE_NUMBER'].shift()).cumsum()
    # groupby
    gb = df.groupby(['CARRIER_NAME', 'CARRIER_BOARD_NUM', changed])
    result = gb.agg({'OFFSET': [list, 'min'], 'ROUTE_NUMBER': 'first', 'ID_STOP': list})

    # flatten & rename
    result = result.reset_index()
    result.columns = ['_'.join(tup).rstrip('_') for tup in result.columns.values]
    result.rename({'CARRIER_BOARD_NUM': 'vid', 'ROUTE_NUMBER_first': 'route', 'OFFSET_list': 'real_times',
                   'OFFSET_min': 'offset', 'ID_STOP_list': 'stops'}, axis='columns', inplace=True)
    # drop lines with only one stop
    l = result['stops'].apply(len)
    result = result[l > 1]
    print('Estimated', l.sum()-l.shape[0], 'optimizations')

    # remove unneeded columns
    result = result[['vid', 'route', 'offset', 'stops', 'real_times']]
    # order by offset
    result = result.set_index('offset').sort_index()
    return result


df = pd.read_csv(CROPPED_DATASET, sep=';', index_col='STOP_TIME_REAL', parse_dates=['STOP_TIME_REAL'], dayfirst=True)
print(df.columns)
print(f'{df.shape[0]} rows read')

# df = cut_by_time(df)
df = cut_unneeded_stops_and_buses(df)
df = df.apply(disambiguate_route, axis=1)
df = add_offset(df)
df = rename_stops(df)
df = group_routes(df)

df.to_csv(FINAL_DATASET, sep=';', index=True)
print(f'{df.shape[0]} rows written')

# print(df)