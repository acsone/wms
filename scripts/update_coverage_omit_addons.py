#!/usr/bin/env python
import ast
import os

import click

COVERAGE_FILE_PATH = ".coveragerc"
COVERAGE_EXCLUDE_SEPARATOR = "# NOT INSTALLABLE ADDONS"
COVERAGE_EXCLUDE_SEPARATOR_END = "# END NOT INSTALLABLE ADDONS"

MANIFEST_NAMES = ("__manifest__.py", "__openerp__.py", "__terp__.py")


class NoManifestFound(Exception):
    pass


def get_manifest_path(addon_dir):
    for manifest_name in MANIFEST_NAMES:
        manifest_path = os.path.join(addon_dir, manifest_name)
        if os.path.isfile(manifest_path):
            return manifest_path


def parse_manifest(s):
    return ast.literal_eval(s)


def read_manifest(addon_dir):
    manifest_path = get_manifest_path(addon_dir)
    if not manifest_path:
        raise NoManifestFound("no Odoo manifest found in %s" % addon_dir)
    with open(manifest_path) as mf:
        return parse_manifest(mf.read())


def is_not_installable_addon(addon_dir):
    try:
        manifest = read_manifest(addon_dir)
    except NoManifestFound:
        return False
    return not manifest.get("installable", True)


@click.command()
@click.option("--addons-dir", default="")
def main(addons_dir):
    """ Update .coveragerc omit section with the list of
        uninstallable addons. The section must begin with a line
        containing '# NOT INSTALLABLE ADDONS' and end with a line
        containing '# END NOT INSTALLABLE ADDONS'.
    """
    not_installable_addons = []
    addons = os.listdir(addons_dir or ".")
    for addon in addons:
        addon_dir = os.path.join(addons_dir, addon)
        if is_not_installable_addon(addon_dir):
            exclude_addon = "    {addon_dir}/*".format(addon_dir=addon_dir)
            not_installable_addons.append(exclude_addon)
    not_installable_addons.sort()
    not_installable_addons_COVERAGE = "\n".join(not_installable_addons)
    if not_installable_addons_COVERAGE:
        not_installable_addons_COVERAGE += "\n"
    replace_on = False
    with open(COVERAGE_FILE_PATH, "r+") as COVERAGE_file:
        COVERAGE_file_lines = COVERAGE_file.readlines()
        COVERAGE_file.seek(0)
        for line in COVERAGE_file_lines:
            if COVERAGE_EXCLUDE_SEPARATOR_END in line:
                replace_on = False
            if replace_on:
                continue
            if COVERAGE_EXCLUDE_SEPARATOR in line:
                replace_on = True
                COVERAGE_file.write(line)
                COVERAGE_file.write(not_installable_addons_COVERAGE)
                continue
            COVERAGE_file.write(line)
        COVERAGE_file.truncate()


if __name__ == "__main__":
    main()