import copy
import traci

class BaseSimulation:
    DEBUG = False
    STATE = []
    CLI_CMD = 'sumo'
    GUI_CMD = 'sumo-gui'
    CHECKPOINTS_DIR = '/home/madis/SUMO/checkpoints/'
    t = None

    def __init__(self, *, cfg=None, net=None, routes=None, additionals=None, teleport_raise=True, state=None, t=None, is_done=None):
        assert cfg is not None or net is not None, 'A config or a net must be given.'
        routes = routes or []
        additionals = additionals or []
        self.desired_t = t
        self.raise_on_teleport = teleport_raise
        self.custom_is_done = is_done
        self.cmd_options = []

        teleport_params = ['--collision.action', 'none', '--max-num-teleports', '1']
        self.cmd_options.extend(teleport_params)
        output_params = ['--no-step-log', 'true']
        self.cmd_options.extend(output_params)
        # other_params = ['--threads', '4']
        # self.cmd_options.extend(other_params)
        if state:
            self.cmd_options.extend(['--load-state', state])

        if cfg is not None:
            self.cmd_options.extend(['-c', cfg])
        else:
            self.cmd_options.extend(['-n', net])
            self.cmd_options.extend(['-r', ','.join(routes)])
            self.cmd_options.extend(['-a', ','.join(additionals)])

        # print(' '.join(self.cmd_options))


    def start(self, *, gui=False, label='default'):
        sumo = self.GUI_CMD if gui else self.CLI_CMD
        cmd = [sumo] + self.cmd_options
        print('Starting simulation:', cmd)
        traci.start(cmd, label=label)
        t = int(traci.simulation.getTime())
        assert self.desired_t is None or t == self.desired_t, f'Wrong time on starting. TraCI {t}, you: {self.desired_t}'
        self.t = t

    def stop(self):
        traci.close()
        print('Simulation took {} steps'.format(self.t))

    def restart(self, **kwargs):
        if self.DEBUG:
            print('Restarting simulation')
        self.stop()
        # clearing the state
        for a in self.STATE:
            try:
                getattr(self, a).clear()
            except AttributeError:
                setattr(self, a, kwargs.pop(a, None))
        self.start()

    @property
    def is_done(self):
        s = traci.simulation
        return s.getCurrentTime() > 0 and s.getMinExpectedNumber() == 0

    def step(self):
        if self.t is None:
            self.t = int(traci.simulation.getTime())
        traci.simulationStep()
        self.t += 1
        self.on_step(traci)

    def on_step(self, traci):
        pass

    def checkpoint(self, name):
        path = f'{self.CHECKPOINTS_DIR}{name}.st.xml'
        traci.simulation.saveState(path)

        return dict(state=path, t=self.t, **{k: copy.deepcopy(getattr(self, k)) for k in self.STATE})

    def run_until_time(self, t):
        print(f'Running until time {t}')
        assert t >= self.t, f'Time is in the past. me: {self.t}, given {t}'
        while self.t < t:
            self.step()

    def run_until_done(self):
        print('Running until done')
        while not ((self.custom_is_done and self.custom_is_done(self)) or self.is_done):
            self.step()

