#!/usr/bin/env python
import argparse
import ast
import os
import re

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


def get_oca_addon_in_requirements(requirement_file):
    """Return the addon names in the requirements file.

    We consider that an addon in the requirements file is an OCA addon.
    """
    oca_addons = []
    with open(requirement_file) as f:
        for line in f:
            if line.startswith("odoo-addon-"):
                module_name = line.split()[0].replace("odoo-addon-", "")
                # remove the part after "=="
                module_name = module_name.split("==")[0]
                module_name = module_name.replace("-", "_")
                oca_addons.append(module_name)
    return oca_addons


def main(addons_dir, requirements_file):  # noqa: C901
    """Update manifest files to sort dependencies by typa and then by name.

    This script will sort the dependencies of all manifest files in the given
    directory. We'll get 3 groups of dependencies: custom, OCA and others.

    The script will also exclude not installable addons from the dependencies.
    """
    oca_addons = get_oca_addon_in_requirements(requirements_file)
    addons = os.listdir(addons_dir or ".")
    for addon in addons:
        addon_dir = os.path.join(addons_dir, addon)
        try:
            manifest = read_manifest(addon_dir)
        except NoManifestFound:
            continue
        if not manifest.get("installable", True):
            continue
        dependencies = manifest.get("depends", [])
        custom = []
        oca = []
        other = []
        for dep in dependencies:
            if dep in addons:
                custom.append(dep)
            elif dep in oca_addons:
                oca.append(dep)
            else:
                other.append(dep)
        custom = sorted(custom)
        oca = sorted(oca)
        other = sorted(other)
        dependencies = custom + oca + other
        dependencies_excluded = ",\n".join([f"        '{dep}'" for dep in dependencies])
        if dependencies_excluded:
            dependencies_excluded += "\n"
        manifest_path = get_manifest_path(addon_dir)
        with open(manifest_path) as f:
            content = f.read()
        # We want to replace the line "depends": ["add2", "add1", "add3"] or "depends": [\n"add2",\n"add1",\n"add3"\n]
        # with "depends": [\n"add1",\n"add2",\n"add3",\n]
        pattern = r'"depends":\s*\[([^]]*)\]'
        new_content = '"depends": ['
        new_content += "\n        # fmt: off"
        if custom:
            new_content += (
                "\n        # Custom\n        "
                + ",\n        ".join(f'"{dep}"' for dep in custom)
                + ","
            )
        if oca:
            new_content += (
                "\n        # OCA\n        "
                + ",\n        ".join(f'"{dep}"' for dep in oca)
                + ","
            )
        if other:
            new_content += (
                "\n        # Others\n        "
                + ",\n        ".join(f'"{dep}"' for dep in other)
                + ","
            )
        new_content += "\n        # fmt: on"
        new_content += "\n    ]"
        content = re.sub(pattern, new_content, content, flags=re.DOTALL)
        with open(manifest_path, "w") as f:
            f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--addons-dir")
    parser.add_argument("--requirements-file")
    args = parser.parse_args()
    main(args.addons_dir, args.requirements_file)
