import pytest

from sproing import container
from sproing import dependency
from sproing.container import SproingNamedDependencyError, SproingDependencyError
from sproing.dependency import SproingDependencyDefinitionError, SproingDependency, SproingLazyDependencyDefinitionError


def test_dependency(initialize):
    def sample_dependency(arg_a: str, agr_b: int) -> str:
        ...

    dependency(sample_dependency)

    assert str in container.dependencies


def test_container_dependency(initialize):
    def sample_dependency() -> str:
        ...

    dependency(sample_dependency)

    dep = container.dependencies[str][0]
    assert dep.provider == sample_dependency
    assert dep.name == sample_dependency.__name__


def test_dependency_missing_return_hint(initialize):
    with pytest.raises(SproingDependencyDefinitionError) as excinfo:
        def sample_dependency():
            ...

        dependency(sample_dependency)

        expected = ("Error validating return type for dependency "
                    "'sample_dependency': No return type hint provided.")
        assert expected in excinfo.value


def test_dependency_missing_parameter_hint(initialize):
    with pytest.raises(SproingDependencyDefinitionError) as excinfo:
        def sample_dependency(parameter) -> str:
            ...

        dependency(sample_dependency)

        expected = ("Error validating argument 'parameter' for dependency "
                    "'sample_dependency': No type hint provided.")
        assert expected in excinfo.value


def test_named_dependency(initialize):
    def sample_dependency() -> str:
        ...

    dependency(sample_dependency, name="named_dependency")

    assert "named_dependency" in container.named_dependencies

    dep = container.named_dependencies["named_dependency"]
    assert dep.provider == sample_dependency
    assert dep.name == sample_dependency.__name__


def test_named_dependency_declared_twice(initialize):
    def first_dependency() -> str:
        ...

    dependency(first_dependency, name="named_dependency")

    with pytest.raises(SproingNamedDependencyError) as excinfo:
        def second_dependency() -> str:
            ...

        dependency(second_dependency, name="named_dependency")

        expected = ("Error registering dependency 'second_dependency'. "
                    "Another dependency is already using the name: 'named_dependency'.")
        assert expected in excinfo.value


def test_primary_dependency(initialize):
    def primary_dependency() -> str:
        ...

    dependency(primary_dependency, primary=True)

    assert str in container.primaries
    assert type(container.primaries[str]) == SproingDependency


def test_primary_named_dependency(initialize):
    def primary_dependency() -> str:
        ...

    with pytest.raises(SproingDependencyError) as excinfo:
        dependency(primary_dependency, primary=True, name="named_dependency")

        expected = ("Error registering dependency 'primary_dependency'. "
                    "A dependency cannot be both primary and named.")

        assert expected in excinfo.value


def test_singleton_dependency(initialize):
    value = 0

    def singleton_dependency() -> int:
        nonlocal value
        value += 1
        return value

    sproing_dependency = dependency(singleton_dependency, singleton=True)

    assert sproing_dependency() == 1
    assert sproing_dependency() == 1


def test_not_singleton_dependency(initialize):
    value = 0

    def singleton_dependency() -> int:
        nonlocal value
        value += 1
        return value

    sproing_dependency = dependency(singleton_dependency, singleton=False)

    assert sproing_dependency() == 1
    assert sproing_dependency() == 2


def test_lazy_singleton(initialize):
    value = 0

    def sample_dependency() -> int:
        nonlocal value
        return value

    sproing_dependency = dependency(sample_dependency, singleton=True, lazy=True)

    value = 1
    assert sproing_dependency() == 1
    assert sproing_dependency() == 1


def test_not_lazy_factory(initialize):
    def sample_dependency() -> int:
        ...

    with pytest.raises(SproingLazyDependencyDefinitionError) as excinfo:
        dependency(sample_dependency, singleton=False, lazy=False)

        expected = ("Error defining dependency 'sample_dependency' lazyness: "
                    "must be lazy when not singleton.")
        assert expected in excinfo.value
