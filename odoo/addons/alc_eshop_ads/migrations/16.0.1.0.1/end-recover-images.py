import logging

from openupgradelib import openupgrade

from odoo import fields

from odoo.addons.fs_image.fields import FSImageValue

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Migrate Ads Image to right storage")
    now = fields.Datetime.now()
    domain = [("date_start", "<=", now), ("date_end", ">=", now)]
    for ads in env["alc.eshop.ads"].search(domain):
        if ads.image and not ads.image.url:
            _logger.info("Migrate Ads Image to right storage for %s", ads.name)
            name = ads.image.name
            ads.image = FSImageValue(name=name, data=ads.image.getvalue())
    _logger.info("Migrate Ads Image to right storage done")
