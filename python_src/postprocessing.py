import traci
import pandas as pd
import pygal
from pygal.style import CleanStyle as style
from simulation.specific import BusSimulation

PATH = '../results/result_fight_2.log'
with open('../dataset/buses.dsv') as f:
    DATA = f.readlines()
DATA = list(map(lambda x: x.strip().split(';'), DATA[1:]))

def demo():
    s = BusSimulation(net='../SUMO/short_added_net/short_added.net.xml',
                      additionals=['../SUMO/short_added_net/short_added_stops.xml'],
                      routes=['../SUMO/short_added_net/short_added.buses.rou.xml',
                              '../SUMO/short_added_net/short_added.cars_v2.rou.xml',
                              '../results/fight_1_result.rou.xml'],
                      data=DATA, teleport_raise=False
                      )
    s.start(gui=True)
    s.vs = []
    while not s.is_done:
        s.step()
        c = traci.vehicle.getIDCount()
        s.vs.append(c)
    s.stop()
    return s

df = pd.read_csv(PATH, sep=',', skipinitialspace=True,
                 names=['vid', 'route', 'stop_time', 'next_stop', 'niter', 'zero_f_value', 'f_value'],
                 converters={'vid': lambda x: x.split()[1]}, na_values='None')
print(df.dtypes)

# 1. Status diagram -- OK
df['status'] = 'Invalid'
df['status'][df.niter == 1] = 'No improvement'
df['status'][df.f_value<df.zero_f_value] = 'Improvement'
df['status'][df.f_value<10] = 'Success'
print(df)

status = df['status'].value_counts().sort_index().reset_index()
print(status)
print('Total simulations', df.status.sum())

chart = pygal.Bar(title='Optimizations by status')
for row in status.values:
    # print(row)
    chart.add(str(row[0]), row[1])
chart.render_to_png('../results/1_status.png', style=style)

valid = df[df['status'] != 'Invalid']

# 2. result at fixed stop pair
vosst_1 = valid[(valid['next_stop'] == 'suvorov_0') & (valid['route'].isin(['24_b', '27_b', '191_b']))].reset_index()
print(vosst_1)
chart = pygal.StackedBar(title='F-value at vosst_0 -> suvorov_0')
chart.add('f_value', vosst_1.f_value.values)
chart.add('zero_f_value', (vosst_1.zero_f_value-vosst_1.f_value).values)
chart.render_to_png('../results/2_vosst_f_value.png', style=style)

# 3. Error by (route, stop)
# was: Error in ALL valid simulations
chart = pygal.StackedBar(title='Results of modelling')
by_route_stop = valid.groupby(['route', 'next_stop']).agg({'f_value': 'mean', 'zero_f_value': 'mean'})
# chart.add('No cars added', (df.zero_f_value-df.f_value).values)
# chart.add('Cars added', df.f_value.values)
chart.add('f_value', by_route_stop.f_value.values)
chart.add('zero_f_value', (by_route_stop.zero_f_value-by_route_stop.f_value).values)
chart.render_to_png('../results/3_global_result.png', style=style)

print('Total iterations', valid.niter.sum())
print('to be done: ncars graph')

s = demo()

# 4. Vehicles in each step of the simulation -- OK
chart = pygal.Bar(title='# vehicles during result simulation')
# chart.add('No cars added', (df.zero_f_value-df.f_value).values)
# chart.add('Cars added', df.f_value.values)
chart.add('Vehicles', s.vs)
chart.render_to_png('../results/4_n_vehicles.png', style=style)


buses = pd.DataFrame()
buses['vid'] = list(s.buses.keys())
buses['route'] = buses['vid'].apply(lambda vid: s.buses[vid].route_name)
buses['total_error'] = buses['vid'].apply(lambda vid: s.buses[vid].get_total_error())
buses['last_error'] = buses['vid'].apply(lambda vid: s.buses[vid].get_error_at_last_stop())
buses['travel_time'] = buses['vid'].apply(lambda vid: s.buses[vid].get_total_travel_time())
buses['real_travel_time'] = buses['vid'].apply(lambda vid: s.buses[vid].get_real_total_travel_time())
# total_error = sum(total_errors)
# last_errors = [bus.get_error_at_last_stop() for bus in s.buses.values()]
# last_error = sum(last_errors)
print('Total error:', buses.total_error.sum())
print('Sum last stop error:', buses.last_error.sum())

# 5. Avg total error by route
# was: Total error by bus (all)
by_route = buses.groupby('route').agg({'total_error': 'mean', 'last_error': 'mean', 'travel_time': 'mean', 'real_travel_time': 'mean'})
chart = pygal.Bar(title='Total error by route')
chart.add('Error', by_route.total_error.values)
chart.render_to_png('../results/5_total_errors.png', style=style)

# 5a. Avg last stop error by route
# was: last stop error by bus (all\
chart = pygal.Bar(title='Last stop error by route')
chart.add('Error', by_route.last_error.values)
chart.render_to_png('../results/5a_last_stop_errors.png', style=style)

# 6. Get total travel time
# travel_times = [bus.get_total_travel_time() for bus in s.buses.values()]
chart = pygal.Bar(title='Travel time by route')
chart.add('simulation', by_route.travel_time.values)
chart.add('real', by_route.real_travel_time.values)
chart.render_to_png('../results/6_travel_times.png', style=style)
