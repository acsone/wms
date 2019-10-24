<!--
This file has been generated with 'invoke project.sync'.
Do not modify. Any manual change will be lost.
Please propose your modification on
https://github.com/camptocamp/odoo-template instead.
-->
# How to initialize a migration project

## Initialization steps

### Create the new branch

First step is to create the new branch for the new version.

Generally the branch is created from master and takes the name of the new version.
By example `12.0` for a migration to version 12.

For next steps:

* Don't commit directly on that new branch, but propose a pull request on it.
* Use different commit for each action to help reviewers understand your changes,
  because finally the pull request will contain a lot of files changed.

### Convert the project to new version

Next step is to convert the project to new version.

Actions to do are:

1. Generate the project in new version from odoo-template
2. Override all current files with the new version generated.

   From original code:
   * Keep specific modules, move them in `local-src` if needed, and make them uninstallable.
   * Check which songs we want to keep and adapt them to be played in `setup` version.
   * Remove all other files we don't have in new version.

3. Edit the `.gitmodules` to choose which modules we want to keep.
4. Initialize submodules.

   _DO NOT initialize submodules before to avoid to manage changes of version for each submodule._
5. Test and fix the build

### Switch branches

Default branch for developments is `master`.

When the build is finally OK and dependencies (minions, integrations, ...) too:

* Create a branch from master to save the old version (eg: `8.0`) and push 
* Create a pull request from new version branch to master
* Merge the new branch into master

Finally, we have a branch for the old version and master for the new version.

## Tools/Scripts to help the developer

### Invoke task to convert the project to new version

See documentation of task:
* [invoke.md](invoke.md#migrateconvert-project)

Limitations and optimizations:

* Works only with a docker project
* Need an adaptation for old projects
* A new option to keep modules list in `migration.yml` can be cool
  (keep the template version of file and just add modules into).
* Optimize the code if possible
* ...
