# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests

from odoo import _, api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


def online(link):
    try:
        return requests.get(link, timeout=10).status_code == 200
    except requests.exceptions.RequestException:
        return False


class ProductTemplate(ProductTemplateBase):

    link_info = fields.Char("Additional information link", translate=True)
    link_video = fields.Char("Video link", translate=True)
    link_notice = fields.Char("Notice link", translate=True)
    links_offline = fields.Char(
        "Offline Links",
        store=True,
        compute="_compute_links_offline",
        help="Filled links for info or video or notice are offline?",
    )

    @api.model
    def _cron_check_links_online(self, force=False):
        domain_to_check = [
            "|",
            "|",
            ("link_info", "!=", False),
            ("link_notice", "!=", False),
            ("link_video", "!=", False),
        ]
        if not force:
            domain_to_check = ["&", ("links_offline", "=", False), *domain_to_check]
        to_check = self.search(domain_to_check)
        for product in to_check:
            description = _("Check online links for product {product_name}.").format(
                product_name=product.name
            )
            product.with_delay(description=description)._compute_links_offline()

    @api.depends("link_info", "link_notice", "link_video")
    def _compute_links_offline(self):
        link_fields = {"link_info", "link_notice", "link_video"}
        langs = [code_name[0] for code_name in self.env["res.lang"].get_installed()]
        for rec in self:
            # changing the lang and reading the value of the translation seems causing
            # cache issue and the value of the field is lost,
            # env.protecting should resolve this but didn't
            # dump solution is to snapshot values and reset the cache
            values = {field: rec[field] for field in link_fields}
            product = rec.with_context(lang=False)
            links = {link_field: product[link_field] for link_field in link_fields}
            for lang in langs:
                product_lang = product.with_context(lang=lang)
                for field in link_fields:
                    if product_lang[field] and product_lang[field] != links[field]:
                        links[field + "_" + lang] = product_lang[field]
            offline = [fl for fl in links if links[fl] and not online(links[fl])]
            values["links_offline"] = ", ".join(offline) if offline else False
            rec.update(values)
