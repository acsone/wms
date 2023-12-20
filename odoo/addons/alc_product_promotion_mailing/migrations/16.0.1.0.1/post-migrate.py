from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.load_data(
        cr, "alc_product_promotion_mailing", "data/queue_job_channel.xml", mode="init"
    )
