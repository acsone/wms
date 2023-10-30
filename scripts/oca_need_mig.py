#!/usr/bin/env python
"""Find out if OCA addons have migration scripts, by trying to download.

the wheel and looking for the migrations directory.

Read addons names, from stdin, outputs oca.csv.
"""
import csv
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile


def oca_needs_mig(addon_name, odoo_version, venv):
    dist_name = f"odoo{odoo_version}-addon-{addon_name}"
    with tempfile.TemporaryDirectory() as tmpdir:
        r = subprocess.call(
            [
                venv / "bin" / "python",
                "-m",
                "pip",
                # "-q",
                "download",
                "--index",
                "https://wheelhouse.odoo-community.org/oca-simple",
                "--extra-index-url",
                "https://wheelhouse.shopinvader.com/simple",
                "--extra-index-url",
                "https://wheelhouse.acsone.eu/acsone-simple",
                "--no-deps",
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


with open("oca.csv", "a") as f:
    writer = csv.DictWriter(
        f,
        [
            "addon_name",
            "mig_status_11",
            "mig_status_12",
            "mig_status_13",
            "mig_status_14",
            "mig_status_15",
        ],
    )
    writer.writeheader()
    with venvs() as venv:
        for line in sys.stdin:
            addon_name = line.strip()
            if addon_name.startswith("#"):
                continue
            print(addon_name, "... ", file=sys.stderr, end="")
            row = {"addon_name": addon_name}
            for odoo_version in (11, 12, 13, 14, 15):
                mig_status = oca_needs_mig(addon_name, odoo_version, venv)
                row[f"mig_status_{odoo_version}"] = mig_status
            print(row, file=sys.stderr)
            writer.writerow(row)
