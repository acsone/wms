#!/usr/bin/env python
import argparse
import ast
import os

FILE_PATH = "pyproject.toml"
EXCLUDE_SEPARATOR = "# MYPY NOT INSTALLABLE ADDONS"
EXCLUDE_SEPARATOR_END = "# MYPY END NOT INSTALLABLE ADDONS"

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


def main(addons_dir):
    """Update pyproject.tom  [MYPY] exclude section with the list of.

    uninstallable addons. The section must begin with a line
    containing '# MYPY NOT INSTALLABLE ADDONS' and end with a line
    containing '# MYPY END NOT INSTALLABLE ADDONS'.
    """
    not_installable_addons = []
    addons = os.listdir(addons_dir or ".")
    for addon in addons:
        addon_dir = os.path.join(addons_dir, addon)
        if is_not_installable_addon(addon_dir):
            exclude_addon = f"  '{addon_dir}/*'"
            not_installable_addons.append(exclude_addon)
    not_installable_addons.sort()
    not_installable_addons_excluded = ",\n".join(not_installable_addons)
    if not_installable_addons_excluded:
        not_installable_addons_excluded += "\n"
    replace_on = False
    with open(FILE_PATH, "r+") as toml_file:
        toml_file_lines = toml_file.readlines()
        toml_file.seek(0)
        for line in toml_file_lines:
            if EXCLUDE_SEPARATOR_END in line:
                replace_on = False
            if replace_on:
                continue
            if EXCLUDE_SEPARATOR in line:
                replace_on = True
                toml_file.write(line)
                toml_file.write(not_installable_addons_excluded)
                continue
            toml_file.write(line)
        toml_file.truncate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--addons-dir")
    args = parser.parse_args()
    main(args.addons_dir)
