# Szczepienia.pw end-to-end tests
End to end tests written in Python ***unittest*** framework using ***selenium*** and ***mysql*** modules that test complete flows of the [szczepienia.pw](https://github.com/szczepienia-pw) web application.

## Prerequisites
This test suite assumes that there is a working:
- szczepienia.pw frontend;
- szczepienia.pw backend;
- mysql server with an initialized database

at a specified address.

## Usage
Before running the test, some parameters have to be specified:
- frontend url;
- backend url;
- mysql server host;
- mysql server user and password;
- database name.

Those params can be provided in two ways:
1. by editing the `default.json` file;
2. by using commandline arguments - those **override** settings from `defaults.json`.

### Selected commandline arguments
1. `--front_url` - frontend url
2. `--back_url` - backend url
3. `--db_address` - mysql server hostname
4. `--db_user` - database user
5. `--db_passwd` - database password
6. `--db_name` - database name
7. `--headless` | `--no-headless` - indicate headless/non-headless mode

All the commandline arguments from the `unittest` framework can be used as well. Unknown arguments will cause errors in the `unittest` framework. Please find all additional information using:

> ```python ./szczepienia.test.py --help```

### Running the tests
To run all tests execute:
> `python3 ./szczepienia.test.py`

**[NOT RECOMMENDED]**

It is also possible to run all the test in a way enabled by the `unittest` framework:

> `python3 -m unittest`

however this way is highly not recommended - defaults are loaded from `defaults.json` and no commandline arguments other than those from the `unittest` framework take effect.

### Running only chosen tests
It is possible to run only a chosen test suite, or a chosen test.

1. Running a chosen suite:
    > `python3 ./szczepienia.test.py TestSuiteName`
    
    e.g.:
    > `python3 ./szczepienia.test.py AdminTests` 

2. Running a chosen test:
    > `python3 ./szczepienia.test.py TestSuiteName.test_name`
    
    e.g.:
    > `python3 ./szczepienia.test.py AdminTests.test01_admin_login`

## Development
1. Every test suite should be in a separate file, named `test_*.py`. Each test suite is a separate class, inherited from the `unittest` base class. It should be named `*Tests`.
2. Every test's name has to start with a `test*_` prefix.
3. It is recommended to impose an order in which the tests will be executed, in order to do so please use prefixes: `test01_`, `test02_`, etc. for the test names.

## CI/CD Effort
Those tests are to be included in our CI/CD pipelines by the end of the fourth sprint.
