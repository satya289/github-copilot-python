import random
import pytest

from app import CURRENT, app


@pytest.fixture(autouse=True)
def reset_current_and_seed():
    """Reset the in-memory CURRENT state and seed randomness for deterministic tests.

    This fixture runs automatically for every test to ensure tests are isolated from
    global state and that puzzle generation is deterministic during a test run.
    """
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    CURRENT['hints_used'] = 0
    # Seed the global RNG so puzzle generation is deterministic in CI/locally
    random.seed(0)
    yield
    # Ensure state is reset after the test as well
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    CURRENT['hints_used'] = 0
