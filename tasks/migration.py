# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from invoke import task, exceptions

import sys
try:
    import psycopg2
except ImportError:
    psycopg2 = None
try:
    import pyodbc
except ImportError:
    pyodbc = None
try:
    import odoorpc
except ImportError:
    odoorpc = None


def disable_mto(odoo):
    """ MTO has to be 'disabled' during the import of sale orders
    we need to reactivate it later

    We change the procurement rules to avoid creation of purchase orders.
    Thus to do this we change the behavior of those rules to act like MTS only.
    Which should only generate pickings on no purchase orders.

    """
    xmlids = [
      '__setup__.procurement_rule_materiel_mto_mtu',
      '__setup__.procurement_rule_ali_mto_mtu',
      '__setup__.procurement_rule_medoc_mto_mtu',
      '__setup__.procurement_rule_froid_mto_mtu',
    ]
    for xid in xmlids:
        proc_rule = odoo.env.ref(xid)
        proc_rule.action = 'move'


def enable_mto(odoo):
    """ MTO is 'disabled' during the import of sale orders
    we need to reactivate it later

    """
    xmlids = [
      '__setup__.procurement_rule_materiel_mto_mtu',
      '__setup__.procurement_rule_ali_mto_mtu',
      '__setup__.procurement_rule_medoc_mto_mtu',
      '__setup__.procurement_rule_froid_mto_mtu',
    ]
    for xid in xmlids:
        proc_rule = odoo.env.ref(xid)
        proc_rule.action = 'split_procurement'


def _connect(url, username, password, database, use_ssl, port):
    if not odoorpc:
        raise Exception("Missing 'odoorpc' dependency. Please install it.")
    protocol = 'jsonrpc'
    if use_ssl:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        protocol += '+ssl'
    odoo = odoorpc.ODOO(url, protocol, port)
    odoo.login(database, username, password)
    return odoo


@task(name="pre")
def pre(
        ctx, url='temp-pp-erp.alcyonbelux.be',
        username='admin', password='admin',
        database='temp-odoo-preprod', use_ssl=True, port=443):
    """ Do pre migration tasks

    - Disable MTO
    """
    odoo = _connect(url, username, password, database, use_ssl, port)
    disable_mto(odoo)


@task(name="post")
def post(
        ctx, url='temp-pp-erp.alcyonbelux.be',
        username='admin', password='admin',
        database='temp-odoo-preprod', use_ssl=True, port=443):
    """ Do post migration tasks

    - Enable MTO
    """
    odoo = _connect(url, username, password, database, use_ssl, port)
    enable_mto(odoo)
