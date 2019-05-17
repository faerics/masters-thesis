class Route(dict):
    def __call__(self, **kwargs):
        return dict(self, **kwargs)


# routes
f0a = Route(name='f0a', max_ncars=70, rewind=10) # was 500
f0_ = Route(name='f0*', max_ncars=50, rewind=30)
f0b = Route(name='f0b', max_ncars=100, rewind=0) # was 150
f1 = Route(name='f1', max_ncars=100, rewind=10) # was 100, rewind as f0a
f2a = Route(name='f2a', max_ncars=40, rewind=20)
f2b = Route(name='f2b', max_ncars=70, rewind=0) # was 150, rewind as f0b
f2c = Route(name='f2c', max_ncars=40, rewind=5)
f2d = Route(name='f2d', max_ncars=40, rewind=5)
f3a = Route(name='f3a', max_ncars=30, rewind=5) # was 250! rewind as f2d
f3b = Route(name='f3b', max_ncars=50, rewind=5) # was 150, rewind as f2c
f4 = Route(name='f4', max_ncars=30, rewind=10) # rewind as f0a
f4_ = Route(name='f4*', max_ncars=55, rewind=0)
f5 = Route(name='f5', max_ncars=70, rewind=20)
f6a = Route(name='f6a', max_ncars=50, rewind=10) # rewind as f0a
f6b = Route(name='f6b', max_ncars=40, rewind=20) # rewind as f5
f8a = Route(name='f8a', max_ncars=20, rewind=0)
f8b = Route(name='f8b', max_ncars=20, rewind=0)


MAPPING = {
    ('liteyny_0', 'vosst_0'): [f0a, f0_(rewind=5), f1],
    ('liteyny_0', 'mayakovskogo'): [f4, f4_, f6a],
    ('vosst_0', 'railway_0'): [f3b, f8b, f8a],
    ('vosst_0', 'suvorov_0'): [f0a(rewind=70), f0_, f8a], # need big offset
    ('mayakovskogo', 'zhukovskogo_22'): [f4_],
    ('suvorov_0', 'poltav_0'): [], # need TL adjustment
    ('suvorov_1', 'railway_0'): [f0b, f2b],

    ('bkz', 'railway_0'): [f8a, f3b], # no f0a need big offset
    ('bkz', 'vosst_1'): [f2c, f3b],
    ('railway_1', 'vosst_1'): [f2d, f3a], # с лиговского сверху на невский
    ('railway_1', 'suvorov_0'): [f2a], # no f0a, too big offset,
    ('suvorov_1', 'vosst_1'): [f0b],
    ('poltav_1', 'suvorov_1'): [], # need TL adjustment,
    ('vosst_1', 'liteyny_1'): [f5, f6b],
    ('vosst_1', 'liteyny_2'): [f5, f6b],
    ('liteyny_2', 'zhukovskovgo_15'): [], # used as a speed tester

    # f3a not needed because of bus route
}

if __name__ == '__main__':
    d = Route(a=1, b=2)
    d(b=3)
    print(d)
    print(MAPPING[('liteyny_0', 'vosst_0')]['rewind'])