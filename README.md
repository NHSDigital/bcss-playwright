# BCSS Playwright Test Suite

[![CI/CD Pull Request](https://github.com/nhs-england-tools/repository-template/actions/workflows/cicd-1-pull-request.yaml/badge.svg)](https://github.com/nhs-england-tools/playwright-python-blueprint/actions/workflows/cicd-1-pull-request.yaml)

This repository contains the automated UI test suite for the BCSS application, built using [Playwright Python](https://playwright.dev/python/). It provides a structured framework and reusable utilities to support consistent, maintainable test development across the project.

Playwright is the recommended UI testing tool for NHS England, as outlined on the [NHS England Tech Radar](https://radar.engineering.england.nhs.uk/), and has been adopted here to modernize and streamline our testing workflows.


# Origin of the Framework

This framework was originally based on the NHS England Playwright Python Blueprint and has since been tailored to meet the specific needs of the BCSS application. While the core utilities and conventions remain, the project has been extended with custom page object models (POMs) and new utility modules to support BCSS-specific workflows, data handling, and UI interactions.

Note: This project is actively maintained and evolving.

# Table of Contents

- [BCSS Playwright Test Suite](#bcss-playwright-test-suite)
- [Origin of the Framework](#origin-of-the-framework)
- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
    - [1. Install Python 3.11 or higher](#1-install-python-311-or-higher)
    - [2. Set up a virtual environment (recommended)](#2-set-up-a-virtual-environment-recommended)
      - [First Create the virtual environment](#first-create-the-virtual-environment)
      - [Next Activate the virtual environment](#next-activate-the-virtual-environment)
    - [3. Install Playwright browser binaries](#3-install-playwright-browser-binaries)
  - [Installation \& Configuration](#installation--configuration)
    - [1. Install Dependencies](#1-install-dependencies)
    - [2. Environment Variables](#2-environment-variables)
    - [3. Test Configuration](#3-test-configuration)
  - [Running Tests](#running-tests)
    - [1. Basic Test Execution](#1-basic-test-execution)
    - [2. Test Filtering](#2-test-filtering)
    - [3. Viewing Trace Files](#3-viewing-trace-files)
  - [Test Structure and Conventions](#test-structure-and-conventions)
    - [1. File Organization](#1-file-organization)
    - [2. Naming Conventions](#2-naming-conventions)
    - [3. Test Function Anatomy](#3-test-function-anatomy)
    - [4. Markers and Tags](#4-markers-and-tags)
    - [5. Skipping and Expected Failures](#5-skipping-and-expected-failures)
  - [Page Object Model (POM) Guidelines](#page-object-model-pom-guidelines)
    - [1. What is a POM?](#1-what-is-a-pom)
    - [2. Location and Structure](#2-location-and-structure)
    - [3. Naming Convention](#3-naming-convention)
    - [4. Anatomy of a Page Class](#4-anatomy-of-a-page-class)
  - [Utility Modules](#utility-modules)
    - [1. Purpose of Utility Modules](#1-purpose-of-utility-modules)
    - [2. Example: Wait Utility](#2-example-wait-utility)
    - [3. Best Practices](#3-best-practices)
    - [4. Blueprint Utilities](#4-blueprint-utilities)
  - [Contributing](#contributing)
  - [Contacts](#contacts)
  - [Licence](#licence)

# Getting Started

## Prerequisites

Follow these steps to make sure your system is ready to run the BCSS test framework. 

### 1. Install Python 3.11 or higher

This framework is built using Python, so you'll need to install it first. You can download the latest version from the official [Python](https://www.python.org/downloads/) website.

To check if Python is already installed, open a terminal or command prompt and run:

`python --version`

### 2. Set up a virtual environment (recommended)

A virtual environment is like a sandbox—it keeps your project’s Python packages separate from everything else on your computer. This prevents version conflicts and makes your setup easier to manage.

Note: If you are using an IDE such as Visual Studio Code or PyCharm, you will normally be prompted to do this automatically.

#### First Create the virtual environment

To create and activate a virtual environment, open your terminal or command prompt in the root folder of the project (where requirements.txt lives), then run:

`python -m venv .venv`

This creates a folder called .venv that contains a clean Python environment just for this project.

If you get an error like 'python not found', try using python3 instead:

`python3 -m venv .venv`

#### Next Activate the virtual environment

This step tells your terminal to use the Python version and packages inside .venv.

On Windows (Command Prompt):

`.venv\Scripts\activate`

On Windows (PowerShell):

`.venv\Scripts\Activate.ps1`

On macOS/Linux:

`source .venv/bin/activate`

Once activated, your terminal will show the virtual environment name (e.g. (.venv)), indicating you're working inside it.

### 3. Install Playwright browser binaries

Playwright uses real browsers to run tests. You’ll need to install these browser binaries once by running:

`playwright install`

This downloads the necessary versions of Chromium, Firefox, and WebKit so tests can run across different browser types.

## Installation & Configuration

### 1. Install Dependencies

Before configuring anything, make sure all required packages are installed by running:

`pip install -r requirements.txt`
`playwright install --with-deps`

(If you're running on Windows or macOS locally, `playwright install` alone is often enough. The `--with-deps` flag is most useful in Linux-based environments or CI pipelines.)

This installs all Python dependencies listed in the `requirements.txt` file, including Playwright and any custom utilities used in the BCSS framework.

Note: If you're using a virtual environment (recommended), activate it before running the install command (see previous steps).

### 2. Environment Variables

Create a `.env` file in the project root to store sensitive configuration values like credentials, URLs, or feature flags. Example:

```
BASE_URL=https://bcss.example.com
USERNAME=test_user
PASSWORD=secure_password123
```

These variables are loaded automatically by the framework using python-dotenv, keeping secrets out of the codebase.
The actual values required for the `.env` file can be obtained from one of the testers already using this framework.
Important Note: Ensure that `.env` is added to your `.gitignore` to avoid accidentally committing secrets. 

### 3. Test Configuration

You can test the configuration has worked by running our example tests, which can be done using the following command (this will run all tests with tracing reports turned on, and in headed mode so you can see the browser execution):

`pytest --tracing on --headed`

Alternatively if you are using Visual Studio Code as your IDE, we have pre-configured this project to work with the
[Testing functionality](https://code.visualstudio.com/docs/editor/testing) so the example tests should be discovered automatically.

## Running Tests

### 1. Basic Test Execution

To run all tests with tracing enabled:

`pytest --tracing on`

To run a specific test file:

`pytest tests/test_login.py --tracing on`

Tracing captures detailed information about each test run, including browser actions, network requests, and DOM snapshots.

### 2. Test Filtering

Use markers or keywords to run subsets of tests:

`pytest -m "smoke" --tracing on`
`pytest -k "login" --tracing on`

You can combine flags like `-v (verbose)` and `--maxfail=1` to control output and failure behavior:

`pytest -v --maxfail=1 --tracing on`

### 3. Viewing Trace Files

After running tests with tracing enabled, trace files are saved in the test-results folder.

To view a trace:

Open https://trace.playwright.dev/

Drag and drop the .zip file from the test-results folder into the browser window

Use the interactive viewer to explore browser actions, network activity, and DOM snapshots

This is especially useful for debugging failed tests or understanding complex UI flows.

## Test Structure and Conventions

### 1. File Organization

All tests are located in the tests/ directory.

Each feature or module has its own test file, e.g.:

`test_login.py`

`test_user_profile.py`

### 2. Naming Conventions

Test files: test_<feature>.py
Example: test_login_to_bcss.py

Page Object Models: <page>_page.py
Example: login_failure_screen_page.py


### 3. Test Function Anatomy

Each test typically follows this structure:

```python
def test_user_can_login(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("user@example.com", "securepassword")
    assert login_page.is_logged_in()
```

- Use Page Object Model (POM) for UI interactions

- Keep assertions clear and focused

- Avoid hardcoded waits - prefer expect() or Playwright’s built-in waiting mechanisms

### 4. Markers and Tags

Use @pytest.mark.<tag> to run a subset or tests as required:

```python
@pytest.mark.smoke
def test_basic_login(page):
```

So for example running `pytest -m "smoke" --tracing on` will only run tests that have the 'smoke' mark.

pytest marks are defined in the `pytest.ini` file.

Common tags:
smoke: quick validation of core functionality
regression: full suite for release validation
slow: long-running tests

### 5. Skipping and Expected Failures

Use Pytest decorators to manage test behavior:

```python
@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature(page):


@pytest.mark.xfail(reason="Known bug in login flow")
def test_login_with_invalid_credentials(page):
```

## Page Object Model (POM) Guidelines

### 1. What is a POM?
A Page Object Model is a design pattern that encapsulates UI interactions for a specific page or component into a dedicated class. This keeps test code clean, readable, and reusable.

Instead of writing raw selectors and actions in your test, you use methods from a page class:

```python
def test_user_can_login(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("user@example.com", "securepassword")
    assert login_page.is_logged_in()
```

### 2. Location and Structure

All POMs are stored in the pages/ directory.

Each file represents a single page or component, for example:

- login_page.py
- dashboard_page.py
- user_profile_page.py

### 3. Naming Convention

- Class names: LoginPage, DashboardPage, etc.
- File names: lowercase with underscores, matching the class name (e.g. login_page.py)

### 4. Anatomy of a Page Class

```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("button[type='submit']")

    def navigate(self):
        self.page.goto("https://bcss.example.com/login")

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def is_logged_in(self):
        return self.page.locator("text=Welcome").is_visible()
```

## Utility Modules

Utility modules help you abstract common functionality that doesn’t belong in a specific page class. This keeps your POMs lean and your tests DRY (Don’t Repeat Yourself).

### 1. Purpose of Utility Modules

- Handle reusable actions (e.g. login, file uploads, date pickers)
- Provide custom assertions or wait conditions
- Manage test data generation or environment setup

### 2. Example: Wait Utility

```python
# utils/wait_utils.py

from playwright.sync_api import expect

def wait_for_element(page, selector, timeout=5000):
    expect(page.locator(selector)).to_be_visible(timeout=timeout)
```

### 3. Best Practices

- Keep utilities modular and single-purpose.
- Avoid hardcoding values—use config files or environment variables.
- Document each function with a short docstring.
- Use type hints for clarity and IDE support.

### 4. Blueprint Utilities

This blueprint provides the following utility classes, that can be used to aid in testing:

| Utility                                                       | Description                                  |
| ------------------------------------------------------------- | -------------------------------------------- |
| [Axe](./docs/utility-guides/Axe.md)                           | Accessibility scanning using axe-core.       |
| [Date Time Utility](./docs/utility-guides/DateTimeUtility.md) | Basic functionality for managing date/times. |
| [NHSNumberTools](./docs/utility-guides/NHSNumberTools.md)     | Basic tools for working with NHS numbers.    |
| [User Tools](./docs/utility-guides/UserTools.md)              | Basic user management tool.                  |

## Contributing

Further guidance on contributing to this project can be found in our [contribution](./CONTRIBUTING.md) page.

## Contacts

If you have any ideas or require support for this project, please [raise an issue via this repository](https://github.com/nhs-england-tools/playwright-python-blueprint/issues/new/choose) using the appropriate template.

If you have any general queries regarding this blueprint, please contact [dave.harding1@nhs.net](mailto:dave.harding1@nhs.net).

## Licence

Unless stated otherwise, the codebase is released under the [MIT License](LICENCE.md). This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown Copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
