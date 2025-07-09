"""
This is a conftest.py file for pytest, which is used to set up fixtures and hooks for testing.
This file is used to define fixtures that can be used across multiple test files.
It is also used to define hooks that can be used to modify the behavior of pytest.
"""

import pytest
import os
from dotenv import load_dotenv
from pathlib import Path
from utils.load_properties_file import PropertiesFile

LOCAL_ENV_PATH = Path(os.getcwd()) / "local.env"


@pytest.fixture(autouse=True, scope="session")
def import_local_env_file() -> None:
    """
    This fixture is used to import the local.env file into the test environment (if the file is present),
    and will populate the environment variables prior to any tests running.
    If environment variables are set in a different way when running (e.g. via cli), this will
    prioritise those values over the local.env file.

    NOTE: You should not use this logic to read a .env file in a pipeline or workflow to set sensitive values.
    """
    if Path.is_file(LOCAL_ENV_PATH):
        load_dotenv(LOCAL_ENV_PATH, override=False)


@pytest.fixture
def smokescreen_properties() -> dict:
    return PropertiesFile().get_smokescreen_properties()


@pytest.fixture
def general_properties() -> dict:
    return PropertiesFile().get_general_properties()


from typing import Any
import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest


def pytest_addoption(parser: Parser) -> None:
    """
    Add custom command-line options to pytest.

    Args:
        parser (Parser): The pytest parser object used to define CLI options.

    Adds:
        --subjects-to-run-for (int):
            The number of subjects to run the test setup for.
            Default is 10.

    Example:
        pytest tests/test_setup.py::test_setup_subjects_as_a259 --subjects-to-run-for=5
    """
    parser.addoption(
        "--subjects-to-run-for",
        action="store",
        default="10",
        help="Number of subjects to run the test setup for (default: 10)",
    )


@pytest.fixture
def subjects_to_run_for(request: FixtureRequest) -> int:
    """
    Fixture to retrieve the value of the '--subjects-to-run-for' CLI argument.

    Args:
        request (FixtureRequest): Provides access to the requesting test context.

    Returns:
        int: The number of subjects specified via the CLI or default (10).
    """
    return int(request.config.getoption("--subjects-to-run-for"))  # type: ignore
