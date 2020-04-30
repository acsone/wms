from ConfigParser import ConfigParser

from setuptools import setup

cfg = ConfigParser()
cfg.read('../acsoo.cfg')


setup(
    version=cfg.get('acsoo', 'series') + '.' + cfg.get('acsoo', 'version'),
    name='odoo-addons-alcyon',
    description='Alcyon Odoo Addons',
    setup_requires=['setuptools-odoo'],
    odoo_addons={'odoo_version_override': '10.0'},
    install_requires=['odoo-autodiscover', 'click-odoo-contrib>=1.10.1'],
)
