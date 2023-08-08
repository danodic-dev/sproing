from container import dependency, dependencies, inject


class Hey:
    pass


@dependency
def sample_dep() -> Hey:
    return Hey()


@inject
def test(a: Hey):
    print(a)


if __name__ == '__main__':
    test()
