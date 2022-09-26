#!/usr/bin/env python
import os
import subprocess
import sys

import click


@click.command()
@click.argument("modules")
@click.option("--directory", "-d", type=click.Path(exists=True), required=True, default="odoo/addons")
@click.option("--init-version-name", default="10.0")
@click.option("--target-version-name", default="16.0")
@click.option("--format-patch", is_flag=True)
def main(modules, directory, init_version_name, target_version_name, format_patch):
    cmd = [
        "odoo-module-migrate",
        "--directory",
        directory,
        "--modules",
        modules,
        "--init-version-name",
        init_version_name,
        "--target-version-name",
        target_version_name,
    ]
    if format_patch:
        cmd.append("--format-patch")
    r = subprocess.call(cmd)
    sys.exit(r)
