import os

from .call import check_call


def mkvenv(dirname, python, pip_installs=None):
    check_call(["rm", "-rf", dirname])
    check_call(["virtualenv", dirname, "-p", python])
    check_call(
        [
            os.path.join(dirname, "bin", "python"),
            "-m",
            "pip",
            "install",
            "pip",
            "--upgrade",
        ]
    )
    if pip_installs:
        for pip_install in pip_installs:
            check_call(
                [
                    os.path.join(dirname, "bin", "python"),
                    "-m",
                    "pip",
                    "install",
                    *pip_install,
                ]
            )
