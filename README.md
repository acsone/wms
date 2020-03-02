[![Build Status](https://travis-ci.com/camptocamp/alcyon_odoo.svg?token=3A3ZhwttEcmdqp7JzQb7&branch=master)](https://travis-ci.com/camptocamp/alcyon_odoo)

# Alcyon Odoo

**Our internal id for this project is: 1793.**

This project uses Docker.
Travis builds a new image for each change on the branches and for each new tag.

The images built on the master branch are built as `camptocamp/alcyon_odoo:latest`.
The images built on other branches are built as `camptocamp/alcyon_odoo:<branch-name>`.
The ones built from tags are built as `camptocamp/alcyon_odoo:<tag-name>`.

Images are pushed on the registry only when Travis has a green build.

When a container starts, the database is automatically created and the
migration scripts automatically run.

## Project maintenance

Please keep this project up-to-date by:

* ensure the `FROM` image in `odoo/Dockerfile` is the latest release
* run regularly `invoke project.sync` to retrieve the last template's changes

## Development environment howto (with pip)

### Initialize virtualenv

Create and activate virtualenv, possibly with virtualenvwrapper's
`mkvirtualenv odoo-alcyon -a . --python=$(which python3)`

If you plan to pip install git reference without `-e` you must also upgrade pip with 

```bash
pip install -U git+https://github.com/pypa/pip@refs/pull/7612/head
``` 

 (this is only necessary for `pip freeze` to work with git references without `-e, the caching part is already in pip 20.0).

### Install everything

```bash
cd setup
pip install -r requirements.txt -e .
```

### Run

```bash
odoo
```

### Develop

This project uses [black](https://github.com/psf/black) as code formatting convention.
To make sure local coding convention are respected before you commit, install
[pre-commit](https://github.com/pre-commit/pre-commit) and run `pre-commit install`
after cloning the repository.

### Release

#### To release manually

* update version in `./acsoo.cfg`
* commit everything
* into the setup directory run `pip wheel -r requirements.txt -e . --wheel-dir=./release`

## Links
* [General documentation](./docs/README.md)
* [Local documentation](./docs/README.local.md)
* [Changelog](HISTORY.rst).
* [Minions](https://alcyon_odoo.odoo-test.camptocamp.ch)
* [Base image documentation](https://github.com/camptocamp/docker-odoo-project)
