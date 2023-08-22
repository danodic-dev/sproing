import pytest

from sproing.container import initialize_container


@pytest.fixture
def initialize():
    initialize_container()
