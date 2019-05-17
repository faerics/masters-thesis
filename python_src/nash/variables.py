from secrets import SystemRandom
random = SystemRandom()

# print('Importing variables!')
class Variable:
    new_value = None
    value = None

    def fix(self):
        assert self.new_value is not None
        assert self.new_value != self.value
        self.value = self.new_value
        self.new_value = None

    def _perturb(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def is_valid(self, value):
        return value != self.value

    def next(self):
        new_value = self._perturb()
        while not self.is_valid(new_value):
            new_value = self._perturb()

        self.new_value = new_value
        return self.new_value

class Discrete(Variable):
    def __init__(self, options):
        self.options = tuple(set(options))
        self.value = random.choice(options)

    def _perturb(self):
        return random.choice(self.options)

    def reset(self):
        return random.choice(self.options)


class Continuous(Variable):
    def __init__(self, min_init, max_init, *, factor=.05):
        self.min, self.max = min_init, max_init
        assert self.min < self.max
        self.value = random.uniform(self.min, self.max)
        self.factor = factor

    @property
    def delta(self):
        bound = self.factor*self.value
        return random.uniform(-bound, bound)

    def is_valid(self, value):
        return super().is_valid(value) and value >= self.min and value <= self.max

    def _perturb(self):
        return self.value + self.delta

    def reset(self):
        self.value = random.uniform(self.min, self.max)
        return self.value

class Integer(Variable):
    #TODO: DRY!
    def __init__(self, min_init, max_init, *, min_delta=1, factor=.05):
        self.min, self.max = int(min_init), int(max_init)
        self.min_delta = min_delta
        assert self.min < self.max
        self.value = random.randint(self.min, self.max)
        self.factor = factor

    @property
    def delta(self):
        # TODO that's not a min delta actually
        bound = max(self.min_delta, int(self.factor*self.value))
        return random.randint(-bound, bound)

    def is_valid(self, value):
        return super().is_valid(value) and value >= self.min and value <= self.max

    def _perturb(self):
        return self.value + self.delta

    def reset(self):
        self.value = random.randint(self.min, self.max)
        return self.value

class IncreasingInteger(Integer):
    #TODO: DRY!
    def __init__(self, min_init, max_init, *, factor=.05, min_delta=2):
        super().__init__(min_init, max_init, factor=factor)
        self.min_delta = min_delta
        self.value = self.min

    @property
    def delta(self):
        bound = max(1, int(self.factor * self.value))
        rand_delta = random.randint(self.min_delta, self.min_delta+2)
        return rand_delta if rand_delta > bound else random.randint(self.min_delta, bound)

    def is_valid(self, value):
        return value == self.max or super().is_valid(value)

    def _perturb(self):
        return min(self.value + self.delta, self.max)

    def fix(self):
        super().fix()
        self.static = self.value >= self.max

    def reset(self):
        self.value = random.randint(self.min, self.value)
        return self.value

def is_variable(v):
    # return type(v) is Continuous
    return isinstance(v, Variable)