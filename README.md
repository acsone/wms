# Alcyon Odoo

## Development environment howto (with pip)

### Initialize virtualenv

Create and activate virtualenv, possibly with virtualenvwrapper's
`mkvirtualenv odoo-alcyon -a . --python=$(which python2)`

Make sure you have `pip>=20.1` installed in your virtualenv (using `pip list`).

### Install everything

```bash
pip install -e . -c requirements.txt --pre
```

### Run

```bash
odoo
```

## Develop

This project uses [black](https://github.com/psf/black) as code formatting convention.
To make sure local coding convention are respected before you commit, install
[pre-commit](https://github.com/pre-commit/pre-commit) and run `pre-commit install`
after cloning the repository.

## Running tests

- `pip install -r requirements-test.txt pytest-odoo`
- run tests as usual with `odoo --test-enable`
- to run tests with pytest Odoo, `pip install pytest-odoo`
  `pytest --odoo-database=<dbname> "--ignore-glob=**/manual_tests" odoo/addons`
  should work (note the ignore of the `manual_tests` directory)

## Release

* commit everything
* run `bumpversion patch`
* run `acsoo tag` which will push a tag and trigger a build; depending on
  the environment the deployment will be automatic, or need a manual action
  in the GitLab pipeline to trigger it
