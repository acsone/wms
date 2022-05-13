# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import job


def online(link):
    try:
        return requests.get(link).status_code == 200
    except requests.exceptions.RequestException:
        return False


class ProductTemplate(models.Model):

    _inherit = "product.template"

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
    def cron_check_links_online(self, force=False):
        domain_to_check = [
            "|",
            "|",
            ("link_info", "!=", False),
            ("link_notice", "!=", False),
            ("link_video", "!=", False),
        ]
        if not force:
            domain_to_check = ["&", ("links_offline", "=", False)] + domain_to_check
        to_check = self.search(domain_to_check)
        for product in to_check:
            description = _("Check online links for product %s.") % product.name
            product.with_delay(description=description)._compute_links_offline()

    @job(default_channel="root.background.process")
    @api.depends("link_info", "link_notice", "link_video")
    def _compute_links_offline(self):
        link_fields = {"link_info", "link_notice", "link_video"}
        langs = [code_name[0] for code_name in self.env["res.lang"].get_installed()]
        offlines = {}
        for product in self:
            product = product.with_context(lang=False)
            links = {link_field: product[link_field] for link_field in link_fields}
            for lang in langs:
                product_lang = product.with_context(lang=lang)
                for field in link_fields:
                    if product_lang[field] and product_lang[field] != links[field]:
                        links[field + "_" + lang] = product_lang[field]
            offline = [fl for fl in links if links[fl] and not online(links[fl])]
            offlines[product] = offline
        for product in self:
            offline = offlines[product]
            product.links_offline = ", ".join(offline) if offline else False
