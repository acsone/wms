# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from invoke import task

try:
    import odoorpc
except ImportError:
    odoorpc = None

module_name = 'connector_esb'
all_cron = [
    {'xmlid': 'ir_cron_esb_export_product', 'nextcall': '00:00:00'},
    {'xmlid': 'ir_cron_esb_export_pharmacy', 'nextcall': '00:30:00'},
    {'xmlid': 'ir_cron_esb_export_customer_morning', 'nextcall': '01:00:00'},
    {'xmlid': 'ir_cron_esb_export_customer_afternoon', 'nextcall': '15:30:00'},
    {
        'xmlid': 'ir_cron_esb_export_customer_address_morning',
        'nextcall': '01:15:00',
    },
    {
        'xmlid': 'ir_cron_esb_export_customer_address_afternoon',
        'nextcall': '15:45:00',
    },
    {'xmlid': 'ir_cron_esb_export_promotion_alcyon', 'nextcall': '02:00:00'},
    {'xmlid': 'ir_cron_esb_export_product_price', 'nextcall': '02:30:00'},
    {'xmlid': 'ir_cron_esb_export_special_promotion', 'nextcall': '03:00:00'},
    {'xmlid': 'ir_cron_esb_export_buy_x_get_y', 'nextcall': '03:15:00'},
    {'xmlid': 'ir_cron_esb_export_stock_update', 'nextcall': '03:30:00'},
    {
        'xmlid': 'ir_cron_esb_export_document_zip_morning',
        'nextcall': '04:00:00',
    },
    {
        'xmlid': 'ir_cron_esb_export_document_zip_afternoon',
        'nextcall': '13:00:00',
    },
]
all_timestamps = [
    'connector_esb.esb_timestamp_stock_update',
    'connector_esb.esb_timestamp_product',
    'connector_esb.esb_timestamp_pharmacy',
    'connector_esb.esb_timestamp_customer',
    'connector_esb.esb_timestamp_customer_address',
    'connector_esb.esb_timestamp_promotion_alcyon',
    'connector_esb.esb_timestamp_product_price',
    'connector_esb.esb_timestamp_special_promotion',
    'connector_esb.esb_timestamp_buyx_gety',
    'connector_esb.esb_timestamp_stock_update',
    'connector_esb.esb_timestamp_document_zip',
]


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


@task(name="activate-jobs")
def activate_jobs(
    ctx,
    url='temp-pp-erp.alcyonbelux.be',
    username='admin',
    password='admin',
    database='temp-odoo-preprod',
    use_ssl=True,
    port=443,
):
    """Activate all cron jobs related to the connector."""
    odoo = _connect(url, username, password, database, use_ssl, port)
    for cron_job in all_cron:
        j = odoo.env.ref(module_name + '.' + cron_job['xmlid'])
        j.active = True


@task(name="deactivate-jobs")
def deactivate_jobs(
    ctx,
    url='temp-pp-erp.alcyonbelux.be',
    username='admin',
    password='admin',
    database='temp-odoo-preprod',
    use_ssl=True,
    port=443,
):
    """Deactivate all cron jobs related to the connector."""
    odoo = _connect(url, username, password, database, use_ssl, port)
    for cron_job in all_cron:
        j = odoo.env.ref(module_name + '.' + cron_job['xmlid'])
        j.active = False


@task(name="set-next-execution-day")
def set_next_execution(
    ctx,
    url='temp-pp-erp.alcyonbelux.be',
    username='admin',
    password='admin',
    database='temp-odoo-preprod',
    use_ssl=True,
    port=443,
    execday='YYYY-MM-DD',
):
    """Set the next execution day for all cron job related to the connector."""
    odoo = _connect(url, username, password, database, use_ssl, port)
    try:
        datetime.strptime(execday, '%Y-%m-%d')
    except ValueError:
        print(
            'The next execution day parameter (execday) provided is '
            'incoherent, format must be YYYY-MM-DD. Aborting !'
        )
        exit()
    for cron_job in all_cron:
        j = odoo.env.ref(module_name + '.' + cron_job['xmlid'])
        j.nextcall = execday + ' ' + cron_job['nextcall']


@task(name="set-timestamp")
def set_timestamp(
    ctx,
    url='temp-pp-erp.alcyonbelux.be',
    username='admin',
    password='admin',
    database='temp-odoo-preprod',
    use_ssl=True,
    port=443,
    timestamp='',
):
    """
    Set timestamp for all export to now or the datetime passed as timestamp.
    """
    odoo = _connect(url, username, password, database, use_ssl, port)
    if not timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print(
            "The new timestamp parameter (timestamp) is invalid, its format"
            " should be YYYY-MM-DD HH:MM:SS. Aborting !"
        )
        exit()
    for esb_timestamp in all_timestamps:
        record = odoo.env.ref(esb_timestamp)
        record.last_export = timestamp


@task(name="reset-esbflux")
def reset_esbflux(
    ctx,
    url='temp-pp-erp.alcyonbelux.be',
    username='admin',
    password='admin',
    database='temp-odoo-preprod',
    use_ssl=True,
    port=443,
):
    """
    Reset buyxgety and special promotion flux.
    """
    odoo = _connect(url, username, password, database, use_ssl, port)
    odoo.env['product.supplierinfo.esbflux'].reset_flux()
