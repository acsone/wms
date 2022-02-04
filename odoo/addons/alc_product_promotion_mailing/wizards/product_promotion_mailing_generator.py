# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict, namedtuple
from datetime import timedelta

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import job

PromotionDef = namedtuple(
    "PromotionDef", ["partner_id", "product_id", "date_end", "supplierinfo_id"]
)


class ProductPromotionMailingGenerator(models.TransientModel):

    _name = "product.promotion.mailing.generator"

    def _get_valid_promotions(self):
        """Return a list PromotionDef tuple."""
        nbr_days = self.env[
            "sale.config.settings"
        ].get_nbr_before_end_promotion_mailing()

        today = fields.Date.today()
        end = fields.Datetime.from_string(today) + timedelta(days=nbr_days)
        date_end = fields.Date.to_string(end)
        self.env.cr.execute(
            """
            SELECT
                subscription.partner_id as partner_id,
                subscription.product_id as product_id,
                promo.date_end as date_end,
                promo.id as supplierinfo_id
            FROM
                alc_product_promotion_subscription subscription
                JOIN product_supplierinfo promo ON
                    promo.product_id = subscription.product_id
                    OR promo.product_tmpl_id = subscription.product_tmpl_id
            WHERE
                promo.date_start is not null
                AND promo.date_end >= %(today)s
                AND promo.date_end <= %(date_end)s
                AND promo.reminder_mailing_sent is not true
                AND (
                    ratio_main_product is not null
                    OR
                    discount_sale is not null
                )
        """,
            {"today": today, "date_end": date_end},
        )
        return [PromotionDef(**res) for res in self.env.cr.dictfetchall()]

    @api.model
    def _get_promos_by_partner_id_and_mark_as_processed(self):
        res = defaultdict(list)
        valid_promotions = self._get_valid_promotions()
        processed_suppplierinfo_ids = set()
        for promo_def in valid_promotions:
            res[promo_def.partner_id].append([promo_def.product_id, promo_def.date_end])
            processed_suppplierinfo_ids.add(promo_def.supplierinfo_id)
        self.env["product.supplierinfo"].browse(
            list(processed_suppplierinfo_ids)
        ).write({"reminder_mailing_sent": True})
        return res

    @api.model
    def _generate_promotion_mailing(self):
        for (
            partner_id,
            proms,
        ) in self._get_promos_by_partner_id_and_mark_as_processed().items():
            description = _("Generate promotion mailing for partner_id %s") % partner_id
            self.with_delay(description=description)._send_promotion_mailing(
                partner_id=partner_id, promotions=proms
            )

    @api.model
    def _build_shop_variant_url(self, shopinvader_variant):
        return u"{}/{}/{}".format(
            shopinvader_variant.backend_id.name,
            shopinvader_variant.lang_id.code[:2],
            shopinvader_variant.url_key,
        )

    @api.model
    @job(default_channel="root.background.eshop.mailing")
    def _send_promotion_mailing(self, partner_id, promotions):
        partner = self.env["res.partner"].browse(partner_id)
        if partner.lang and partner.lang != self.env.lang:
            return self.with_context(land=partner.lang).send_promotion_mailing(
                partner_id, promotions
            )
        backend = self.env.ref("alc_eshop.backend")
        # groups products by date
        res = defaultdict(list)
        for product_id, date in promotions:
            res[date].append(product_id)
        # load all shopinvader_variant to get the product url in the right lang
        product_ids = [p[0] for p in promotions]
        shop_variants = self._get_shop_variants(backend, product_ids)
        data_promotions = {}
        for date, product_ids in res.items():
            date_localized = self.env["ir.qweb.field.date"].value_to_html(date, {})
            data_promotions[date_localized] = shop_variants.filtered(
                lambda p, product_ids=product_ids: p.record_id.id in product_ids
            )
        data = {
            "partner": partner,
            "promotions": data_promotions,
            "backend": backend,
            "company": self.env.user.company_id,
            "get_variant_url": self._build_shop_variant_url,
        }
        html = self.env["report"].get_html(
            docids=None, report_name="report_alc_product_promotion_mailing", data=data,
        )

        mail_values = {
            "email_to": partner.email,
            "body_html": html,
            "auto_delete": True,
        }
        email_from = self.env["sale.config.settings"].get_promotion_mailing_email_from()

        if email_from:
            mail_values["email_from"] = email_from
        new_mail = self.env["mail.mail"].create(mail_values)
        new_mail.mail_message_id.subject = _("Alcyon: End of promotion period alert")
        new_mail.send()
        return new_mail

    @api.model
    def _get_shop_variants(self, backend, product_ids):
        """Return the shopinvader variant in the context lang for the given
        product_ids."""
        lang = self.env.lang

        if lang not in backend.lang_ids.mapped("code"):
            lang = "fr_BE"
        lang_id = self.env["res.lang"]._lang_get(code=lang).id
        return self.env["shopinvader.variant"].search(
            [("lang_id", "=", lang_id), ("record_id", "in", product_ids)]
        )
