from sproing import dependency, inject


def test_inject(initialize):
    def sample_dependency() -> str:
        return "world!"

    dependency(sample_dependency)

    @inject()
    def sample(world: str) -> str:
        return f"Hello, {world}"

    assert sample() == "Hello, world!"


def test_multiple_inject(initialize):
    def sample_dependency() -> str:
        return "world!"

    dependency(sample_dependency)

    def another_dependency() -> int:
        return 2

    dependency(another_dependency)

    @inject()
    def sample(world: str, numba: int) -> str:
        return f"Hello, {world} Numba: {numba}."

    assert sample() == "Hello, world! Numba: 2."


def test_inject_primary(initialize):
    def sample_dependency() -> str:
        return "Hello, "

    dependency(sample_dependency)

    def another_dependency() -> str:
        return "world!"

    dependency(another_dependency, primary=True)

    @inject()
    def sample(value: str) -> str:
        return value

    assert sample() == "world!"


def test_inject_implicit_primary(initialize):
    def sample_dependency() -> str:
        return "Hello, "

    dependency(sample_dependency)

    def another_dependency() -> str:
        return "world!"

    dependency(another_dependency)

    @inject()
    def sample(value: str) -> str:
        return value

    assert sample() == "Hello, "


def test_inject_named_dependency(initialize):
    def sample_dependency() -> str:
        return "A"

    dependency(sample_dependency, name="first_dependency")

    def another_dependency() -> str:
        return "B"

    dependency(another_dependency, name="sample_dependency")

    @inject(explicit={"value": "first_dependency"})
    def sample(value: str) -> str:
        return value

    assert sample() == "A"


def test_inject_singleton_dependency(initialize):
    value = 0

    def sample_dependency() -> int:
        nonlocal value
        value += 1
        return value

    dependency(sample_dependency, singleton=True)

    @inject()
    def sample(arg: int) -> int:
        return arg

    assert sample() == 1
    assert sample() == 1


def test_inject_non_singleton_dependency(initialize):
    value = 0

    def sample_dependency() -> int:
        nonlocal value
        value += 1
        return value

    dependency(sample_dependency, singleton=False)

    @inject()
    def sample(arg: int) -> int:
        return arg

    assert sample() == 1
    assert sample() == 2
