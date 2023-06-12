===========
Alcyon Odoo
===========

.. contents::

Development environment howto
=============================

Development requirements
------------------------

- Install pip-deepfreeze [#]_ with ``pipx install pip-deepfreeze``
- Install pip-split-requirements [#]_ with ``pipx install pip-split-requirements``
- Install pip-preserve-requirements [#]_ with ``pipx install pip-preserve-requirements``
- Install bump2version with ``pipx install bump2version``

- To save some time it is recommended to install git-autoshare [#]_ with ``pipx install
  git-autoshare``. Don't forget to configure it according to the documentation.
- git-aggregator [#]_ (``pipx install git-aggregator``) is also occasionally useful to
  combine multiple pull requests into a single branch (see ``gitaggregate.yaml``).

Initialize virtualenv
---------------------

- Create and activate virtualenv, possibly with virtualenvwrapper's
  `mkvirtualenv odoo-alcyon -a . --python=$(which python2)`

Install everything
------------------

Some dependencies are not available on Pypi as manylinux wheels, so you need
to have a C compiler,the Python headers and some additional dev
packages installed in order to compile them. The list of packages can be
found in the `Dockerfile <https://gitlab.acsone.eu/acsone/odoo-alcyon/
-/blob/master/Dockerfile#L32-38>`_

As an alternative, you can reference the wheelhouse from ACSONE in the pip
environment variable before launching the pip-df command::

   export PIP_FIND_LINKS=https://wheelhouse.acsone.eu/manylinux1

In an activated python 3.11 virtualenv, run::

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

To run tests as usual::

    odoo --test-enable

To run tests with pytest Odoo::

    pip install pytest-odoo
    pytest --odoo-database=<dbname> "--ignore-glob=**/manual_tests" odoo/addons

should work (note the ignore of the `manual_tests` directory)

Release
-------

1. First make sure you have been testing using the correct dependencies by
   running ``pip-df sync`` and checking there is no change in ``requirements.txt``.
2. Update the version number using ``bumpversion patch|minor|major`` and push the tag
   that bumpversion created with ``git push --tags``.
2. The deploy to the test environment will be automatic, and GitLab will show buttons
   on the pipeline to deploy to other environments.

.. [#] https://pypi.python.org/pypi/pip-deepfreeze
.. [#] https://pypi.python.org/pypi/pip-preserve-requirements
.. [#] https://pypi.python.org/pypi/pip-split-requirements
.. [#] https://pypi.python.org/pypi/git-autoshare
.. [#] https://pypi.python.org/pypi/git-aggregator
.. [#] https://github.com/ambv/black
.. [#] https://github.com/pre-commit/pre-commit
