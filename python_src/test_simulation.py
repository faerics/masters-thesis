from simulation import Simulation
from simulation.specific import BusSimulation as BS
from vehicles import Bus
import traci

# 0. check that it runs :)
print('Running test 0')
s = Simulation(net='../SUMO/short_added_net/short_added.net.xml',
               additionals=['../SUMO/short_added_net/short_added_stops.xml'],
               routes=['../SUMO/short_added_net/short_added.buses.rou.xml'])
s.start(gui=False)
s.run_until_done()
s.stop()

s = BS(net='../SUMO/short_added_net/short_added.net.xml',
               additionals=['../SUMO/short_added_net/short_added_stops.xml'],
               routes=['../SUMO/short_added_net/short_added.buses.rou.xml'])
s.start(gui=False)
s.run_until_done()
s.stop()


# 1. Get arrival/departure on stop of each bus
# class BusSimulation(Simulation):
#     next_stop_mapping = dict()
#
#     def on_step(self, traci):
#         t = traci.simulation.getTime()
#         for vid in traci.simulation.getDepartedIDList():
#             # print('Added {} ({})'.format(vid, traci.vehicle.getTypeID(vid)))
#             if traci.vehicle.getTypeID(vid) == 'BUS':
#                 stops = traci.vehicle.getNextStops(vid)
#                 if stops:
#                     self.next_stop_mapping[vid] = stops[0][2]
#         for vid in traci.simulation.getStopStartingVehiclesIDList():
#             traci.vehicle.setColor(vid, (255, 0, 0))
#             print(vid, 'arrived to', self.next_stop_mapping[vid], 'at', t)
#         for vid in traci.simulation.getStopEndingVehiclesIDList():
#             traci.vehicle.setColor(vid, (255, 255, 0))
#             stops = traci.vehicle.getNextStops(vid)
#             print(vid, 'departed', self.next_stop_mapping[vid], 'at', t)
#             if stops:
#                 self.next_stop_mapping[vid] = stops[0][2]
#             else:
#                 self.next_stop_mapping[vid] = ''
#
# s = BusSimulation(net='../SUMO/short_added_net/short_added.net.xml',
#                additionals=['../SUMO/short_added_net/short_added_stops.xml'],
#                routes=['../SUMO/short_added_net/short_added.rou.xml'])
# s.start(gui=False)
# s.run_until_done()
# s.stop()

# 2. Get travel time on each pair of stops
print('Running test 2')
class BusSimulation(Simulation):
    buses = dict()

    def on_step(self, traci):
        t = traci.simulation.getTime()
        for vid in traci.simulation.getDepartedIDList():
            if traci.vehicle.getTypeID(vid) == 'BUS':
                route = traci.vehicle.getRouteID(vid)
                self.buses[vid] = Bus(vid, route, t, add_to_traci=False)
        for vid in traci.simulation.getStopStartingVehiclesIDList():
            traci.vehicle.setColor(vid, (255, 0, 0))
            self.buses[vid].arrive(t)
        for vid in traci.simulation.getStopEndingVehiclesIDList():
            traci.vehicle.setColor(vid, (255, 255, 0))
            self.buses[vid].depart(t)
        if t == 20:
            # traci.route.add("trip", [" 143525633", "-427930952#1"])
            traci.vehicle.add('prog_added', '15', typeID='BUS')


s = BusSimulation(net='../SUMO/short_added_net/short_added.net.xml',
                  additionals=['../SUMO/short_added_net/short_added_stops.xml'],
                  routes=['../SUMO/short_added_net/short_added.buses.rou.xml', '../SUMO/short_added_net/short_added.buses_test.rou.xml']
                  )
s.start(gui=False)
s.run_until_done()
s.stop()

s2 = BS(net='../SUMO/short_added_net/short_added.net.xml',
        additionals=['../SUMO/short_added_net/short_added_stops.xml'],
        routes=['../SUMO/short_added_net/short_added.buses.rou.xml', '../SUMO/short_added_net/short_added.buses_test.rou.xml']
        )
s2.start(gui=False)
s2.run_until_done()
s2.stop()

# 458 steps when 1 bus of each veh, 638 if 2 (with default TLS)
print(s.buses['v_22_b'].get_travel_time())  # total travel time
print(s.buses['v_22_b'].offset)  # total travel time
print(s.buses['v_22_b'].get_travel_time('mayakovskogo', 'zhukovskogo_22'))

print('Buses in s:', list(s.buses.keys()))
print('Buses in s1:', list(s2.buses.keys()))
print('Here we do not add the buses via config (those which managed by traci. Uncomment that line at BusSimulation.step() to see equal buses. '
      'It will break functionality of handling delayed buses.')

print(s.buses['v_22_b'].get_travel_time())
print(s.buses['v_22_b'].offset)
print(s.buses['v_22_b'].get_travel_time('mayakovskogo', 'zhukovskogo_22'))

# 3. Add buses with given data
print('Running test 3')
DATA = '''20;3704;191_a;['liteyny_1'];[20]
44;1262;24_a;['poltav_1', 'suvorov_1', 'vosst_1', 'liteyny_1'];[634, 714, 1355, 1539]
1000;3704;191_a;['liteyny_1'];[20]'''.split('\n')
DATA = list(map(lambda x: x.split(';'), DATA))
print(DATA)
data = DATA.copy()

class BusSimulation(Simulation):
    buses = dict()

    def on_step(self, traci):
        t = traci.simulation.getTime()
        # Addition of a bus by config should be handled

        if data and t == int(data[0][0])-1:
            bus = Bus(_id=data[0][1], route=data[0][2], time=int(data[0][0]), stops=eval(data[0][3]), real_times=eval(data[0][4]))
            print(f'Adding bus with vid {bus.vid}')
            self.buses[bus.vid] = bus
            data.pop(0)

        for vid in traci.simulation.getStopStartingVehiclesIDList():
            traci.vehicle.setColor(vid, (255, 0, 0))
            self.buses[vid].arrive(t)
        for vid in traci.simulation.getStopEndingVehiclesIDList():
            traci.vehicle.setColor(vid, (255, 255, 0))
            self.buses[vid].depart(t)

    @property
    def is_done(self):
        s = traci.simulation
        return s.getMinExpectedNumber() == 0 and len(data) == 0


s = BusSimulation(net='../SUMO/short_added_net/short_added.net.xml',
                  additionals=['../SUMO/short_added_net/short_added_stops.xml'],
                  routes=['../SUMO/short_added_net/short_added.buses.rou.xml']
                  )
s.start(gui=False)
s.run_until_done()
s.stop()

s2 = BS(net='../SUMO/short_added_net/short_added.net.xml',
        additionals=['../SUMO/short_added_net/short_added_stops.xml'],
        routes=['../SUMO/short_added_net/short_added.buses.rou.xml'],
        data=DATA
        )
s2.start(gui=False)
s2.run_until_done()
s2.stop()

print('Buses in s:', list(s.buses.keys()))
print('Buses in s2:', list(s2.buses.keys()))

assert s.t == s2.t
assert DATA

# 4. Run until given bus stops & save state
print('Running test 4')
s2 = BS(net='../SUMO/short_added_net/short_added.net.xml',
        additionals=['../SUMO/short_added_net/short_added_stops.xml'],
        routes=['../SUMO/short_added_net/short_added.buses.rou.xml'],
        data=DATA
        )
s2.start(gui=False)
s2.run_until_bus_stops('1262')
assert s2.t == 44
chk = s2.checkpoint('test')
s2.run_until_bus_stops('1262', 'vosst_1')
assert s2.t == 202 # was 214 because of rerouting which is now disabled
s2.stop()

# 5. Get errors
print('Running test 5')
print(s2.buses['1262'].get_error_at_last_stop())
print(s2.buses['1262'].get_error_at_stop('poltav_1'))
print(s2.buses['1262'].get_total_error())

# 6. Load from checkpoint
print('Running test 6')
s2 = BS(net='../SUMO/short_added_net/short_added.net.xml',
        additionals=['../SUMO/short_added_net/short_added_stops.xml'],
        routes=['../SUMO/short_added_net/short_added.buses.rou.xml'],
        **chk)
s2.start(gui=False)
print(s2.t)
assert s2.t == 44

print('Buses in s2:', list(s2.buses.keys()))
print('Data in s2:', s2.data)

# s2.run_until_done()
s2.run_until_bus_stops('1262', 'vosst_1')
assert s2.t == 202
s2.stop()

# 7. Restart & run until time
s = BS(net='../SUMO/short_added_net/short_added.net.xml',
       additionals=['../SUMO/short_added_net/short_added_stops.xml'],
       routes=['../SUMO/short_added_net/short_added.buses.rou.xml', '../SUMO/short_added_net/short_added.cars_v2.rou.xml'],
       data=DATA
      )
s.start()
# s.run_until_done()
s.run_until_bus_stops('1262')
buses = s.buses
t = s.t
s.restart(data=DATA)
assert s.data == DATA
assert s.buses == {}

s.run_until_time(t-10)
assert t-10 == s.t
assert s.buses == buses

# add vehicles on some flow

print()
print('All seems to be OK. The error below could be the bug in traci connection management.')