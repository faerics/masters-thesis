from secrets import SystemRandom
random = SystemRandom()
from variables import is_variable, Continuous, Variable
from math import inf
import variables # required

# assert is_variable(Continuous(1,3))
# print(id(Continuous))


class Nash():
    DEBUG = False

    def __init__(self, params, obj, *, factor=.05):
        # assert is_variable(Continuous(1, 3))
        self.niter = 0
        self.plateau = 0
        self.raw_params = params

        # print(id(Continuous))
        # for k, v in self.params.items():
        #     print(id(Continuous))
        #     assert isinstance(3, int)
        #     print(v, isinstance(v, variables.Variable))
        #     print(type(v))

        self.f = obj
        self.factor = factor
        self.vars = [k for (k, v) in self.raw_params.items() if is_variable(v)]
        # self.vars = self.raw_params.items()
        if self.DEBUG: print('Vars:', self.vars)

        zero_params = {k: 0 for k in self.vars}
        initial_zero_params = self.raw_params.copy()
        initial_zero_params.update(zero_params)
        try:
            self.zero_f_value = self.f(**initial_zero_params)
        except Exception as e:
            # raise ValueError('Exception when computing zero_f_value') from e
            print('zero_f_value is uncomputable')
            self.zero_f_value = None
        if self.DEBUG: print('Zero f-value:', self.zero_f_value)
        # self.params = self._init_params()
        self.params = initial_zero_params
        if self.DEBUG: print('Initial params: ', zero_params)
        # self.f_value = self.f(**self.params)
        self.f_value = self.zero_f_value
        print('Initial f-value:', self.f_value)

    def _init_params(self):
        initial_random_params = {k: self.raw_params[k].reset() for k in self.vars}
        # print(initial_random_params)
        initial_params = self.raw_params.copy()
        initial_params.update(initial_random_params)
        return initial_params

    def _to_change(self):
        vars = list(filter(lambda var: not getattr(self.raw_params[var], 'static', False), self.vars))
        c_bound = max(1, int(self.factor*len(vars)))
        c = random.randint(1, c_bound)
        return random.sample(vars, c)

    def step(self):
        self.niter += 1
        vars_to_change = self._to_change()
        changed_params = {k: self.raw_params[k].next() for k in vars_to_change}
        # print('Vars to change:', vars_to_change)
        if self.DEBUG: print('Changed:', changed_params)
        new_params = self.params.copy()
        new_params.update(changed_params)
        print('Trying:', {k: new_params[k] for k in self.vars})

        try:
            new_f_value = self.f(**new_params)
        except Exception as e:
            print('Exception in f:', type(e), e.args[0])
            print('Iteration', self.niter, 'Current f-value:', self.f_value)
            return

        if new_f_value <= self.f_value:
            print('Good. f-value is {} (was {})'.format(new_f_value, self.f_value))
            self.f_value = new_f_value
            self.params.update(new_params)
            for var in vars_to_change:
                self.raw_params[var].fix()
        if new_f_value == self.f_value:
            self.plateau += 1
        print('Iteration', self.niter, 'Current f-value:', self.f_value)

    def run(self, niter=None, target_f_value=None, plateau=10):
        assert niter is not None or target_f_value is not None
        print('Starting. n_steps = {}, target f-value = {}'.format(niter, target_f_value))
        print()
        if target_f_value is None: target_f_value = -inf
        done = self.zero_f_value is None or self.zero_f_value <= target_f_value

        while not done and self.f_value > target_f_value:
            self.step()
            if niter is not None and self.niter == niter: break
            if self.plateau >= plateau:
                print('Reinitializing...')
                self.params = self._init_params()
                self.plateau = 0

        print()
        print('Done in {} iterations'.format(self.niter))
        print('f-value is {} in {}'.format(self.f_value, {k: self.params[k] for k in self.vars}))
        print('zero f-value:', self.zero_f_value)


if __name__ == '__main__':
    def f(x, y, z):
        return abs(x)**z+2*abs(y)

    # assert is_variable(Continuous(1,3))
    # assert not is_variable(3)
    params = {'x': Continuous(-1000, 1000), 'y': Continuous(-100, 30000), 'z': 3}
    for k, v in params.items():
        print(v, isinstance(v, Variable))
        print(is_variable(v))
    print(params)
    search = Nash(params, f)