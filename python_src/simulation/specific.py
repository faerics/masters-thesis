import traci
from base import BaseSimulation
from copy import deepcopy
from vehicles import Bus

class BusTeleportedError(Exception):
    pass

class BusSimulation(BaseSimulation):
    STATE = ['buses', 'data']

    def __init__(self, *args, **kwargs):
        self.buses = deepcopy(kwargs.pop('buses', dict()))
        self.data = deepcopy(kwargs.pop('data', None))
        super().__init__(*args, **kwargs)

    @property
    def is_done(self):
        s = traci.simulation
        return not self.data and s.getMinExpectedNumber() == 0

    def checkpoint(self, name):
        if self.data:
            if self.DEBUG: print('Data is not empty when doing checkpoint! Adding buses...')
            self.add_all_buses_to_traci()
        return super().checkpoint(name)

    def _handle_new_buses_from_config(self):
        # get all vehicles that have departed
        for vid in traci.simulation.getDepartedIDList():
            if vid not in self.buses:
                # we have a new vehicle. Add bus if needed and do not add to traci as it's already there.
                if traci.vehicle.getTypeID(vid) == 'BUS':
                    route = traci.vehicle.getRouteID(vid)
                    self.buses[vid] = Bus(vid, route, self.t, add_to_traci=False)
            else:
                assert self.buses[vid].need_moving, f'{vid} departed twice!'
                # we have a delayed bus. Just move it to an appropriate position
                self.buses[vid]._move_to_next_stop()

    def _handle_delayed_buses(self):
        for bus in self.buses.values():
            if self.t+1 == bus.offset:
                # it's time to move the bus
                bus._move_to_next_stop()

    def _handle_new_buses_from_data(self):
        assert self.data is not None, 'Data is not set'

        if self.data and self.t == int(self.data[0][0]) - 1:
            datum = self.data.pop(0)
            vid = self._get_free_vid(datum[1])
            # vid = datum[1]
            assert vid not in self.buses, f'{vid} departed twice!'
            bus = Bus(_id=vid, route=datum[2], time=int(datum[0]), stops=eval(datum[3]),
                      real_times=eval(datum[4]))
            if self.DEBUG: print(f'Adding bus with vid {bus.vid} at step {self.t}')
            self.buses[bus.vid] = bus

    def add_all_buses_to_traci(self):
        print('Adding all buses to traci...')
        for datum in self.data:
            vid = self._get_free_vid(datum[1])
            # vid = datum[1]
            # adding the bus in delayed mode
            bus = Bus(_id=vid, route=datum[2], time=int(datum[0]), stops=eval(datum[3]),
                      real_times=eval(datum[4]), delayed=True)
            if self.DEBUG: print(f'Adding bus with vid {bus.vid} at step {self.t} (will depart at {bus.offset})')
            self.buses[bus.vid] = bus
            # stops = traci.vehicle.getNextStops(bus.vid)
            # print('Stops', stops)
        # erasing all the data
        self.data = None

    def _get_free_vid(self, vid):
        prefix = vid
        suffix = 1
        while vid in self.buses:
            vid = f'{prefix}_{suffix}'
            suffix += 1
        return vid

    def _handle_arrive(self):
        for vid in traci.simulation.getStopStartingVehiclesIDList():
            if vid not in self.buses:
                continue
            # set color to red
            traci.vehicle.setColor(vid, (255, 0, 0))
            self.buses[vid].arrive(self.t)

    def _handle_depart(self):
        for vid in traci.simulation.getStopEndingVehiclesIDList():
            if vid not in self.buses:
                continue
            # set color to yellow
            traci.vehicle.setColor(vid, (255, 255, 0))
            self.buses[vid].depart(self.t)

    def _handle_collisions(self):
        collided = traci.simulation.getCollidingVehiclesIDList()
        # split collided into pairs
        pairs = [collided[i:i+2] for i in range(0, len(collided), 2)]
        # a veh may collide in two different internal SUMO stages and we want to remove it only once
        deleted = []
        for vid1, vid2 in set(pairs):
            if vid1 in deleted or vid2 in deleted:
                # we lready deleted one or both
                continue
            if vid1 not in self.buses:
                # the first is a car
                print('Deleting', vid1, 'at step', self.t, 'due to collision')
                traci.vehicle.remove(vid1)
                deleted.append(vid1)
            elif vid2 not in self.buses:
                # the second is a car while the firs is a bus
                print('Deleting', vid2, 'at step', self.t, 'due to collision')
                traci.vehicle.remove(vid2)
                deleted.append(vid2)
            else:
                # both are buses!
                # vid1_stopped, vid2_stopped = list(map(lambda vid: traci.vehicle.isStopped(vid), (vid1, vid2)))
                vid1_offset, vid2_offset = list(map(lambda vid: self.buses[vid].offset, (vid1, vid2)))
                vid = vid1 if vid1_offset > vid2_offset else vid2
                print('Deleting a BUS', vid, 'at step', self.t, 'due to collision')
                traci.vehicle.remove(vid)
                del self.buses[vid]
                deleted.append(vid)

    def _handle_teleports(self):
        for vid in traci.simulation.getStartingTeleportIDList():
            if traci.vehicle.getTypeID(vid) == 'CAR':
                # a car is being teleported -- we delete it
                print('Deleting', vid, 'due to teleporting')
                traci.vehicle.remove(vid)
            elif traci.vehicle.getTypeID(vid) == 'BUS':
                # a bus being teleported -- we raise! ... or we do nothing not to break the main flow
                if self.raise_on_teleport:
                    raise BusTeleportedError(vid)

    def on_step(self, traci):
        if self.data:
            self.add_all_buses_to_traci()
        self._handle_delayed_buses()
        # self._handle_new_buses_from_config()
        # if self.data: self._handle_new_buses_from_data()
        self._handle_collisions()
        self._handle_teleports()
        self._handle_arrive()
        self._handle_depart()

    def run_until_bus_stops(self, vid, stop=None):
        print(f'Running until {vid} stops', 'somewhere' if stop is None else f'at {stop}')
        while vid not in self.buses:
            self.step()
        bus = self.buses[vid]
        if stop is None:
            passed_stops = len(bus.arrived)
            while len(bus.arrived) == passed_stops:
                self.step()
        else:
            assert stop in bus.next_stop_names, f'The bus {vid} will never stop at {stop}'
            while stop not in bus.arrived:
                self.step()

    def run_until_some_bus_stops_or_done(self):
        print('Running until some bus stops')
        stopped = traci.simulation.getStopStartingVehiclesIDList()
        while not stopped and not self.is_done:
            self.step()
            stopped = traci.simulation.getStopStartingVehiclesIDList()

        result = []
        for vid in stopped:
            # (vid, current stop, next stop) if there is a next stop
            # else (vid, current stop)
            result.append((vid, *self.buses[vid].next_stop_names[:2]))
        return result
