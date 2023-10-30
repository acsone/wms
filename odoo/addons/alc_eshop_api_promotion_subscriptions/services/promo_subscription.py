# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class PromoSubscriptionService(Component):
    """Manage subscription to product's promotions."""

    _inherit = "authenticated_partner.mixin"
    _name = "promo.subscription.service"
    _collection = "shopinvader.backend"
    _usage = "promo_subscriptions"

    @restapi.method(
        [(["/<int:product_id>"], "GET")],
        output_param=restapi.CerberusValidator("_get_output_schema"),
    )
    def get(self, product_id):
        """Check if a subscription exists for the given product_id."""
        record = self.env["alc.product.promotion.subscription"].search(
            [("product_id", "=", product_id), ("partner_id", "=", self.partner.id)]
        )
        status = True
        if not record:
            status = False
        return {"status": status}

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search(self, **params):
        """Get all the products the customer has subscribed to."""
        return self._paginate_search(**params)

    @restapi.method(
        [(["/"], "POST")],
        input_param=restapi.CerberusValidator("_create_input_schema"),
        output_param=restapi.CerberusValidator("_create_output_schema"),
    )
    # pylint: disable=method-required-super
    def create(self, product_id):
        """Subscribe the customer to the promotions for the given product.

        id.
        """
        product = self.env["product.product"].browse(product_id)
        self.env["alc.product.promotion.subscription"].subscribe(
            partner=self.partner, product=product
        )
        return {"status": True}

    @restapi.method([(["/<int:product_id>"], "DELETE")])
    def delete(self, product_id):
        """Unsubscribe the customer to the promotions of the given product.

        id.
        """
        product = self.env["product.product"].browse(product_id)
        self.env["alc.product.promotion.subscription"].unsubscribe(
            partner=self.partner, product=product
        )
        return {}

    ############
    # validators
    ############
    def _get_output_schema(self):
        """
        Output validator for the search.

        :return: dict
        """
        return self._get_status_schema()

    def _search_input_schema(self):
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

    def _search_output_schema(self):
        """
        Output validator for the search.

        :return: dict
        """
        promo_schema = self._get_promo_schema()
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": promo_schema},
            },
        }

    def _create_input_schema(self):
        return {
            "product_id": {
                "coerce": to_int,
                "nullable": False,
                "required": True,
                "type": "integer",
            },
        }

    def _create_output_schema(self):
        return self._get_status_schema()

    ################
    # implementation
    ################

    def _get_status_schema(self):
        return {"status": {"type": "boolean", "required": True, "nullable": False}}

    def _get_promo_schema(self):
        """
        Get details about invoice to return.

        (used into validator_return)
        :return: dict
        """
        promo_schema = {
            "product_id": {"type": "integer", "required": True, "nullable": False},
        }
        return promo_schema

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
