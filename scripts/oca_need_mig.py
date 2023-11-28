#!/usr/bin/env python
"""Find out if OCA addons have migration scripts, by trying to download.

the wheel and looking for the migrations directory.

Read addons names, from stdin, outputs oca.csv.
"""
import csv
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile


def oca_needs_mig(addon_name, odoo_version, venv):
    if odoo_version < 15:
        dist_name = f"odoo{odoo_version}-addon-{addon_name}"
    else:
        dist_name = f"odoo-addon-{addon_name}"
    with tempfile.TemporaryDirectory() as tmpdir:
        r = subprocess.call(
            [
                venv / "bin" / "python",
                "-m",
                "pip",
                # "-q",
                "download",
                "--index",
                "https://wheelhouse.odoo-community.org/oca-simple-and-pypi",
                "--extra-index-url",
                "https://wheelhouse.shopinvader.com/simple",
                "--no-deps",
                "--pre",
                dist_name,
            ],
            cwd=tmpdir,
        )
        if r != 0:
            return "no wheel"
        wheel_name = next(Path(tmpdir).glob("*.whl"))
        with ZipFile(wheel_name) as zf:
            names = set(zf.namelist())
            if odoo_version < 10:
                ns = "odoo_addons"
            else:
                ns = "odoo/addons"
            assert f"{ns}/{addon_name}/__init__.py" in names, names
            for name in names:
                if name.startswith(f"{ns}/{addon_name}/migrations"):
                    return "mig"
            return "no"


@contextmanager
def venvs():
    with tempfile.TemporaryDirectory() as venv:
        subprocess.check_call(["virtualenv", "-q", "-p", "python3", venv])
        yield Path(venv)


with open("oca.csv", "w") as f:
    writer = csv.DictWriter(
        f,
        [
            "addon_name",
            "odoo_version",
            "mig_status",
        ],
    )
    writer.writeheader()
    with venvs() as venv:
        for line in sys.stdin:
            line = line.strip()
            if line.startswith("#"):
                continue
            mo = re.match("^odoo[0-9]*[-_]addon[-_]([a-zA-Z-_0-9]+)", line)
            if not mo:
                print("skipping", line, file=sys.stderr)
                continue
            addon_name = mo.group(1).replace("-", "_")
            print(addon_name, "... ", file=sys.stderr)
            for odoo_version in (11, 12, 13, 14, 15, 16):
                mig_status = oca_needs_mig(addon_name, odoo_version, venv)
                row = {
                    "addon_name": addon_name,
                    "odoo_version": odoo_version,
                    "mig_status": mig_status,
                }
                print(row, file=sys.stderr)
                writer.writerow(row)
