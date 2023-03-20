import subprocess
import tempfile
import textwrap

from .console import bold


def check_call(cmd, cwd=None, **kwargs):
    print(bold(" ".join(cmd)))
    subprocess.check_call(cmd, cwd=cwd, **kwargs)


def click_odoo(db, script_text, cmd="venv-16/bin/click-odoo"):
    with tempfile.TemporaryFile() as f:
        f.write(textwrap.dedent(script_text))
        f.flush()
        check_call([cmd, "-d", db, f.name])
