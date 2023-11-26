# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields

from odoo.addons.alc_connector_search_engine_put_script_mixin.models.se_backend import (
    SeBackend as SeBackendBase,
)


class SeBackend(SeBackendBase):

    net_price_sort_script = fields.Text(
        help="Script used in ES query to sort variant by net price.\n "
        "The following paramters are available into the script context:\n"
        "* pricelist_gross: The product pricelist used to get the gross price\n"
        "* pricelist_discount: The alcyon discount pricelist for the user\n"
        "* supplier_promotion: A boolean to know if the partner benefits from"
        "supplier promotion\n"
        "* today: iso date"
    )

    current_price_pipeline_script = fields.Text(
        help="Script executed at indexation and every day to compute the "
        "informations used to compute the price at the script execution "
        "date"
    )

    def create_or_update_net_price_sort_script(self):
        self._put_script("sort-net-price", self.net_price_sort_script)

    def create_or_update_current_price_pipeline_script(self):
        self._put_script("sort-current-price", self.current_price_pipeline_script)

    def cron_execute_pipeline_set_current_price(self):
        product_indexes = self.env["se.index"].search(
            [("model_id.model", "=", "product.product")]
        )
        product_indexes.execute_pipeline_set_current_price()
