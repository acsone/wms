# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Promotion Mailing",
    "description": """
        Alcyon: Send mails to subcribers when a subscription on a produt read
        its end date""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_pricelist_discount",
        "alc_product_promotion_subscription",
        "alc_queue_job_background_channel",
        "fs_product_multi_image",
        "mail",
        "queue_job_cron",
        "sale",
        "shopinvader_product_url",
    ],
    "data": [
        "data/ir_cron.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "views/res_config_settings.xml",
        "security/product_promotion_mailing_generator.xml",
        "reports/report_alc_product_promotion_mailing.xml",
    ],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
