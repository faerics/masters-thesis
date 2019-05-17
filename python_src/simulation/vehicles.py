import traci

class Bus:
    DEBUG = False
    real_times = None

    def __init__(self, _id, route, time, stops=None, real_times=None, delayed=False, add_to_traci=True):
        self.vid = _id
        self.offset = time
        self.route_name = route
        self.last_stop_arr = self.offset
        self.arrived = []
        self.need_moving = None if not stops else True
        self.arr_times = dict()
        self.dep_times = dict()
        self.travel_times = dict()

        if add_to_traci:
            self._add_to_traci()
        if stops:
            # take stops as is and then assert it in moving
            self.next_stop_names = stops
            if not delayed:
                self._move_to_next_stop() # otherwise it will be called later manually
        else:
            # if stops is not truly, take it from traci
            self.next_stop_names = stops or tuple(map(lambda x: x[2], traci.vehicle.getNextStops(self.vid)))

        assert real_times is None or len(real_times) == len(self.next_stop_names), \
            f'Wrong size of real times. {real_times}; {self.next_stop_names}'
        if real_times is not None:
            self.real_times = dict(zip(self.next_stop_names, real_times))
        # print(self,real_times)
        # print(self.vid, self.next_stop_names)

    def _add_to_traci(self, type_id='BUS'):
        if self.need_moving:
            # adding vehicle in the delay mode: 1 sec for moving, 1 sec for stopping
            traci.vehicle.add(self.vid, self.route_name, typeID=type_id, depart=str(self.offset-2))
        else:
            traci.vehicle.add(self.vid, self.route_name, typeID=type_id)

    def _move_to_next_stop(self):
        t = traci.simulation.getTime()
        assert t+1 == self.offset, (f'Trying to move a bus with wrong time. me: {self.offset}, traci: {t}')
        if self.DEBUG: print(f'Moving {self.vid} to next stop at step {t}')
        # get list of stops
        traci_stops = traci.vehicle.getNextStops(self.vid)
        traci_stop_names = tuple(map(lambda x: x[2], traci_stops))

        if self.next_stop_names is not None:
            # check that all the stops are on the root
            assert all([stop in traci_stop_names for stop in self.next_stop_names]), (
                'Stops contains a stop that is not'
                ' on the route by TraCI.'
                f' Traci: {traci_stop_names}, me: {self.next_stop_names}, vid: {self.vid}, reute: {self.route_name}')
            # compute indices to find current stop
            current_stop = self.next_stop_names[0]
            ind = traci_stop_names.index(current_stop)

            # delete all the stops, move the vehicle and add the rest stops
            for stop in traci_stop_names:
                traci.vehicle.setBusStop(self.vid, stop, duration=0)
            traci.vehicle.moveTo(self.vid, traci_stops[ind][0], traci_stops[ind][1])
            for stop in self.next_stop_names:
                traci.vehicle.setBusStop(self.vid, stop, duration=20)
            self.need_moving = False
        else:
            # no stops provided, get it from traci
            self.next_stop_names = traci_stop_names

    def arrive(self, time):
        stop = self.next_stop_names[0]
        if self.DEBUG: print(f'{self.vid} arrives at {stop}. Time is {time}, real is {self.real_times and self.real_times[stop]}')
        self.last_stop_arr = self.arr_times[stop] = time
        if not self.arrived:
            self.travel_times[stop] = time-self.offset
        else:
            prev_stop = self.arrived[-1]
            self.travel_times[stop] = self.arr_times[stop]-self.dep_times[prev_stop]
        self.arrived.append(stop)

    def depart(self, time):
        stop = self.next_stop_names[0]
        self.dep_times[stop] = time
        self.next_stop_names = self.next_stop_names[1:]

    def get_error_at_stop(self, stop):
        assert stop in self.arrived
        return self.real_times[stop] - self.arr_times[stop]

    def get_error_at_last_stop(self):
        return self.get_error_at_stop(self.arrived[-1])

    def get_total_error(self):
        return sum([self.get_error_at_stop(s) for s in self.arrived])

    def get_total_travel_time(self):
        return self.get_travel_time()

    def get_real_total_travel_time(self):
        first, last = self.arrived[0], self.arrived[-1]
        return self.real_times[last]-self.real_times[first]

    def get_travel_time(self, _from=None, to=None):
        _from_ind = None if _from is None else self.arrived.index(_from)+1
        to_ind = None if to is None else self.arrived.index(to)+1
        return sum([self.travel_times[s] for s in self.arrived[_from_ind:to_ind]])

