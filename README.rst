===========
Alcyon Odoo
===========

.. contents::

Development environment howto
=============================

Initialize virtualenv
---------------------

- Create and activate virtualenv, possibly with virtualenvwrapper's
  `mkvirtualenv odoo-alcyon -a . --python=$(which python2)`
- make sure acsoo [#]_ and pip-deepfreeze [#]_ are installed and in your PATH
- to save some time it is recommended to configure git-autoshare [#]_.

Install everything
------------------

In an activated python 3.6 virtualenv, run::

   pip-df sync

When dependencies change, use ``pip-df sync`` again, possibly with
``--update``. Add unmerged VCS dependencies in ``requirements.txt.in``. See the
pip-deepfreeze documentation for more information.

Run
---
 Run::

    odoo -c odoo.cfg

Develop
-------

This project uses Black [#]_ and other code formatters.
To make sure local coding convention are respected before
you commit, install pre-commit [#]_ and
run ``pre-commit install`` after cloning the repository.

Running tests
-------------

This project needs some extra dependencies to run tests. These dependencies
are declared into the ``extras_require`` section of the ``setup.py`` file.
To install these dependencies run::

    pip-df sync --extras tests

When these dependencies change, use ``pip-df sync --extras tests`` again,
possibly with ``--update``.

To run tests as usual::

    odoo --test-enable

To run tests with pytest Odoo::

    pip install pytest-odoo
    pytest --odoo-database=<dbname> "--ignore-glob=**/manual_tests" odoo/addons

should work (note the ignore of the `manual_tests` directory)

Release
-------

First make sure you have been testing using the correct dependencies by
running ``pip-df sync`` and checking there is no change in ``requirements.txt``.

To release using gitlab-ci
--------------------------

- run ``bumpversion patch|minor|major``
- run ``acsoo tag``, the deploy to the test environment will be automatic, and
  gitlab will show a button on the pipeline to deploy to production.

.. [#] https://pypi.python.org/pypi/acsoo/#installation
.. [#] https://pypi.python.org/pypi/pip-deepfreeze
.. [#] https://pypi.python.org/pypi/git-autoshare
.. [#] https://github.com/ambv/black
.. [#] https://github.com/pre-commit/pre-commit