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
        "external_dependencies_override": {
            "python": {
                "shapefile": "pyshp",
                "slugify": "python-slugify",
                "keycloak": "python-keycloak",
            }
        },
    },
    install_requires=[
        "click-odoo-contrib>=1.10.1",
        "odoo-autodiscover",
        "odoo-addons-enterprise",
        "odoo10-addon-slow-statement-logger",
        "odoo10-addon-attachment_s3",
        "xlrd",
        "numpy",  # speedup pyshape
        "odoo10-addon-logging-json",
        "future==0.18.2",  # silently required by keycloak
        "elasticsearch==7.12.1",  # last release compatible with opendistro
    ],
    entry_points="""
        [console_scripts]
        click-odoo-cubiscan-import=scripts.cubiscan_import:main
        click-odoo-gen-logiweb-po=scripts.gen_logiweb_po:main
    """,
    extras_require={
        "tests": [
            "xmlunittest",
            "freezegun==0.3.14",
            "unittest2",
            "responses",
            "coverage",
        ],
        "dev": ["ipython", "pudb"],
    },
)
