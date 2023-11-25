# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict, namedtuple
from datetime import timedelta

from odoo import _, api, fields, models

PromotionDef = namedtuple(
    "PromotionDef", ["partner_id", "product_id", "date_end", "supplierinfo_id"]
)


class ProductPromotionMailingGenerator(models.TransientModel):

    _name = "product.promotion.mailing.generator"
    _description = "Product Promotion Mailing Generator"

    def _get_valid_promotions(self):
        """Return a list PromotionDef tuple."""
        nbr_days = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_product_promotion_mailing.nbr_before_end_promotion_mailing_setting",
                3,
            )
        )

        today = fields.Date.today()
        end = today + timedelta(days=nbr_days)
        date_end = fields.Date.to_string(end)
        self.env["product.supplierinfo"].flush_model()
        self.env["alc.product.promotion.subscription"].flush_model()
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
            description = _(
                "Generate promotion mailing for partner_id %(partner_id)s",
                partner_id=partner_id,
            )
            self.with_delay(description=description)._send_promotion_mailing(
                partner_id=partner_id, promotions=proms
            )

    @api.model
    def _build_shop_variant_url(self, product):
        website_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_product_promotion_mailing.promotion_website_url_setting",
                "https://www.alcyonbelux.be",
            )
        )
        lang_prfx = self.env.lang[:2]
        url_key = product.url_key
        return f"{website_url}/{lang_prfx}/{url_key}"

    @api.model
    # @job(default_channel="root.background.eshop.mailing")
    def _send_promotion_mailing(self, partner_id, promotions):
        partner = self.env["res.partner"].browse(partner_id)
        if partner.lang and partner.lang != self.env.lang:
            return self.with_context(lang=partner.lang)._send_promotion_mailing(
                partner_id, promotions
            )
        # groups products by date
        res = defaultdict(list)
        for product_id, date in promotions:
            res[date].append(product_id)
        # load all shopinvader_variant to get the product url in the right lang
        product_ids = [p[0] for p in promotions]
        product_by_id = {
            p.id: p for p in self.env["product.product"].browse(product_ids)
        }
        data_promotions = {}
        for date, product_ids in res.items():
            date_localized = self.env["ir.qweb.field.date"].value_to_html(date, {})
            data_promotions[date_localized] = [product_by_id[p] for p in product_ids]
        data = {
            "partner": partner,
            "promotions": data_promotions,
            "company": self.env.user.company_id,
            "get_variant_url": self._build_shop_variant_url,
        }
        html, _ext = self.env["ir.actions.report"]._render_qweb_html(
            "alc_product_promotion_mailing.report_action_alc_product_promotion_mailing",
            None,
            data=data,
        )

        mail_values = {
            "email_to": partner.email,
            "body_html": html,
            "auto_delete": True,
        }
        email_from = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_product_promotion_mailing.promotion_mailing_email_from_setting",
                "secretariat@alcyonbelux.be",
            )
        )

        if email_from:
            mail_values["email_from"] = email_from
        new_mail = self.env["mail.mail"].create(mail_values)
        new_mail.mail_message_id.subject = _("Alcyon: End of promotion period alert")
        new_mail.send()
        return new_mail
