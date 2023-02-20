===========
Alcyon Odoo
===========

.. contents::

Development environment howto
=============================

Development requirements
------------------------

- Install pip-deepfreeze with ``pipx install pip-deepfreeze``
- Install pip-split-requirements with ``pipx install pip-split-requirements``
- Install pip-preserve-requirements with ``pipx install pip-preserve-requirements``

Initialize virtualenv
---------------------

- Create and activate virtualenv, possibly with virtualenvwrapper's
  `mkvirtualenv odoo-alcyon -a . --python=$(which python2)`
- make sure acsoo [#]_ and pip-deepfreeze [#]_ are installed and in your PATH
- to save some time it is recommended to configure git-autoshare [#]_.

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

In an activated python 3.10 virtualenv, run::

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
2. Update the version number using ``bumpversion patch`` or ``bumpversion minor``.
2. Create and push a git tag of the form `x.y.z`. The deploy to the test environment
   will be automatic, and GitLab will show a button on the pipeline to deploy to
   production.

.. [#] https://pypi.python.org/pypi/pip-deepfreeze
.. [#] https://pypi.python.org/pypi/pip-preserve-requirements
.. [#] https://pypi.python.org/pypi/pip-split-requirements
.. [#] https://pypi.python.org/pypi/git-autoshare
.. [#] https://github.com/ambv/black
.. [#] https://github.com/pre-commit/pre-commit
