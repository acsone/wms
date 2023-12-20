from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.load_data(
        cr,
        "alc_stock_release_channel_deliver",
        "data/queue_job_channel.xml",
        mode="init",
    )
