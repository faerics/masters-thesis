if __name__ == '__main__':
    import sys
    sys.path.append('nash')

    import nash
    # TODO: fix the import machinery why the below braeks it???
    # from nash.variables import Continuous, is_variable, Variable
    # print(id(nash.variables.Continuous))
    # assert is_variable(Continuous(1,3))
    # assert not is_variable(3)

    # for k, v in params.items():
    #     print(v, isinstance(v, nash.variables.Variable))
    #     print(nash.variables.is_variable(v))

    def f(x, y, z):
        return abs(x)**z+2*abs(y)

    params = {'x': nash.variables.Continuous(-1000, 1000), 'y': nash.variables.Continuous(-100, 30000), 'z': nash.variables.Integer(1, 50)}
    search = nash.Nash(params, f)
    search.run(niter=10)