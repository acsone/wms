# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class PromoSubscriptionService(Component):
    """Manage subscription to product's promotions."""

    _inherit = "base.rest.service"
    _name = "promo.subscription.service"
    _collection = "shopinvader.backend"
    _usage = "promo_subscriptions"

    def get(self, _id):
        """Check if a subscription exists for the given product_id.

        Return 404 if not found
        """
        record = self.env["alc.product.promotion.subscription"].search(
            [("product_id", "=", _id), ("partner_id", "=", self.partner.id)]
        )
        if not record:
            raise MissingError(_("No subscription found for product id %s") % (_id))
        return self._convert_one_record(record)

    def search(self, **params):
        """Get all the products the customer has subscribed to."""
        return self._paginate_search(**params)

    # pylint: disable=method-required-super
    def create(self, product_id):
        """Subscribe the customer to the promotions for the given product
        id."""
        product = self.env["product.product"].browse(product_id)
        record = self.env["alc.product.promotion.subscription"].subscribe(
            partner=self.partner, product=product
        )
        return self._convert_one_record(record)

    def delete(self, _id):
        """Unsubscribe the customer to the promotions of the given product
        id."""
        product = self.env["product.product"].browse(_id)
        self.env["alc.product.promotion.subscription"].unsubscribe(
            partner=self.partner, product=product
        )
        return {}

    ############
    # validators
    ############
    def _validator_get(self):
        return {}

    def _validator_return_get(self):
        """
        Output validator for the search
        :return: dict
        """
        promo_schema = self._get_return_promo_schema()
        schema = {"data": {"type": "dict", "schema": promo_schema}}
        return schema

    def _validator_search(self):
        return {
            "page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 1,
            },
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 10,
            },
            "product_id": {"coerce": to_int, "nullable": True, "type": "integer"},
        }

    def _validator_return_search(self):
        """
        Output validator for the search
        :return: dict
        """
        promo_schema = self._get_return_promo_schema()
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": promo_schema},
            },
        }

    def _validator_create(self):
        return {
            "product_id": {
                "coerce": to_int,
                "nullable": False,
                "required": True,
                "type": "integer",
            },
        }

    def _validator_return_create(self):
        return self._get_return_promo_schema()

    def _validator_delete(self):
        return {}

    def _validator_return_delete(self):
        return {}

    ################
    # implementation
    ################
    def _get_return_promo_schema(self):
        """
        Get details about invoice to return
        (used into validator_return)
        :return: dict
        """
        promo_schema = {
            "product_id": {"type": "integer"},
        }
        return promo_schema

    @property
    def env(self):
        env = self.work.env
        return env

    @property
    def partner(self):
        partner = self.env["res.partner"].browse()
        partner_id = self.work.authenticated_partner_id
        if partner_id:
            partner = partner.browse(partner_id)
        return partner

    def _paginate_search(self, page=1, per_page=10, product_id=None):
        model_obj = self.env["alc.product.promotion.subscription"]
        domain = [("partner_id", "=", self.partner.id)]
        if product_id:
            domain.append(("product_id", "=", product_id))
        total_count = model_obj.search_count(domain)
        records = model_obj.search(domain, limit=per_page, offset=per_page * (page - 1))
        return {"size": total_count, "data": self._to_json(records)}

    def _to_json(self, records):
        res = []
        for rec in records:
            res.append(self._convert_one_record(rec))
        return res

    def _convert_one_record(self, record):
        record.ensure_one()
        return {"product_id": record.product_id.id}
