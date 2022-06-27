# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class SeBackendElasticsearch(models.Model):

    _inherit = "se.backend.elasticsearch"

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

    def _get_es_client(self):
        self.ensure_one()
        with self.work_on(self._name, index=None) as work:
            adapter = work.component(usage="se.backend.adapter")
            return adapter._get_es_client()

    @api.model
    def _scrip_field_json(self, value):
        value = "".join(value.replace('"""', '"').split("\n"))
        return json.loads(value)

    def create_or_update_net_price_sort_script(self):
        client = self._get_es_client()
        client.put_script(
            "sort-net-price", self._scrip_field_json(self.net_price_sort_script)
        )

    def create_or_update_current_price_pipeline_script(self):
        client = self._get_es_client()
        client.ingest.put_pipeline(
            "set-current-price",
            self._scrip_field_json(self.current_price_pipeline_script),
        )

    def cron_execute_pipeline_set_current_price(self):
        shopinvader_variant_model = self.env.ref(
            "shopinvader.model_shopinvader_variant"
        )
        indexes = self.mapped("index_ids").filtered(
            lambda a, model=shopinvader_variant_model: a.model_id == model
        )
        indexes.execute_pipeline_set_current_price()
