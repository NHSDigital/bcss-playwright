# Playwright Python Blueprint

[![CI/CD Pull Request](https://github.com/nhs-england-tools/repository-template/actions/workflows/cicd-1-pull-request.yaml/badge.svg)](https://github.com/nhs-england-tools/playwright-python-blueprint/actions/workflows/cicd-1-pull-request.yaml)

This project is designed to provide a blueprint to allow for development teams to start quickly developing UI tests using [Playwright Python](https://playwright.dev/python/), providing the base framework and utilities to allow for initial focus on writing tests, rather than configuration of the framework itself.

NOTE: This project is currently under initial development so isn't finalised, but should work if you want to experiment with Playwright Python.

> **NOTE: When considering this project, please be advised that currently Playwright is a "proposed" tool within the [NHS England Tech Radar](https://radar.engineering.england.nhs.uk/). Whilst we are taking steps to get Playwright moved to the "mainstream" section of the radar, as it has not yet been formally adopted it is possible that Playwright may not be fully endorsed by NHS England as a standard tool going forward, and using this framework for an NHS England project is currently at your own risk.**

## Table of Contents

- [Playwright Python Blueprint](#playwright-python-blueprint)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Configuration](#configuration)
  - [Getting Started](#getting-started)
  - [Contacts](#contacts)
  - [Licence](#licence)

## Setup

You can clone this whole repository by clicking on the green `Code` button at near the top of the screen, then select either ssh or https, depending on if you have your ssh key setup

### Prerequisites

#### Python3

To utilise the test for the BCSS app you will first of all require python3. The installation method changes based on operating systems but can usually be installed from a software store.

#### Virtual Environment

To avoid conflicts with the rest of the operating system it is reccomended to create a python virtual environment, this isolates any packages installed and makes your life easier. To do that run the following command:

`python -m venv .venv`

This will create a bunch of files under a directory called `.venv` if you are using Visual Studios Code then it should automatically detect this environment and use it, but you may need to restart VSCode to pick up this new virtual environment

#### Python Packages

There are a bunch of packages that are required to run the tests in this repository, they have been tracked in the `requirements.txt` file. To install them run this command:

```bash
pip install -r requirements.txt
```

This will then install all of the dependancies.

#### Playwright

Once all the pre-requisites have been installed then you can install playwright with the following command:

```bash
playwright install --with-deps
```

This will take a while and will install playwright and its browsers which allow it to run the tests.

### Configuration

There is a makefile which has common commands to interface with the repository, to check if the tests are working you can run the command `make test`

There is also a dockerised version which will create a container using podman and run it there, if you dont have a compatible OS or you dont want to install the dependancies directly, however you will need to install podman and podman-build, you can run that with `podman-test`

## Getting Started

> NOTE: This section is currently under development and requires further work, so links to pages within this repository may not be very useful at this stage.

Once you've confirmed your installation is working, please take a look at the following guides on getting started with Playwright Python.

- [Quick Reference Guide](./docs/getting-started/Quick_Reference_Guide.md) for common commands and actions you may regularly perform using this blueprint.
- [Playwright Python documentation](https://playwright.dev/python/docs/writing-tests) guidance on writing tests.

## Contacts

If you have any queries regarding these tests, please contact [dave.harding1@nhs.net](mailto:dave.harding1@nhs.net). or [andrew.cleveland1@nhs.net](mailto:andrew.cleveland1@nhs.net)

## Licence

Unless stated otherwise, the codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown Copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
