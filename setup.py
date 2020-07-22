from ConfigParser import ConfigParser

from setuptools import setup

cfg = ConfigParser()
cfg.read("./acsoo.cfg")


setup(
    version=cfg.get("acsoo", "series") + "." + cfg.get("acsoo", "version"),
    name="odoo-addons-alcyon",
    description="Alcyon Odoo Addons",
    odoo_addons={
        "odoo_version_override": "10.0",
        "external_dependencies_override": {"python": {"shapefile": "pyshp"}},
    },
    install_requires=[
        "click-odoo-contrib>=1.10.1",
        "odoo-autodiscover",
        "odoo-addons-enterprise",
        "odoo10-addon-slow-statement-logger",
        "xlrd",
        "numpy",  # speedup pyshape
        "odoo10-addon-logging-json",
    ],
)
