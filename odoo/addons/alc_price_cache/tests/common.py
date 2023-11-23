# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.queue_job.tests.common import JobMixin


class TestPrices(TransactionCase, JobMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, es_security_no_autosync=True
            )
        )

        cls.cat_1 = cls.env["product.category"].create({"name": "C1"})
        cls.cat_2 = cls.env["product.category"].create({"name": "C2"})

        vals_product_1 = {"name": "P1", "categ_id": cls.cat_1.id, "list_price": 10}
        cls.product_1 = cls.env["product.product"].create(vals_product_1)
        vals_product_2 = {"name": "P2", "categ_id": cls.cat_2.id, "list_price": 20}
        cls.product_2 = cls.env["product.product"].create(vals_product_2)

        cls.cat_price = cls.env["product.price.category"].create({"name": "C"})

        cls.model_pl = cls.env["product.pricelist"]
        cls.model_pl_nodelay = cls.model_pl.with_context(queue_job__no_delay=True)
        cls.model_pl_item = cls.env["product.pricelist.item"]
        cls.model_pl_item_nodelay = cls.model_pl_item.with_context(
            queue_job__no_delay=True
        )

    @classmethod
    def _get_item_vals(cls, pricelist=None, **kwargs):
        vals = {
            "applied_on": "3_global",
            "compute_price": "percentage",
            "percent_price": 10,
        }
        if pricelist:
            vals["pricelist_id"] = pricelist.id
        return dict(vals, **kwargs)

    @classmethod
    def _get_pricelist_vals(cls, name, item_val_list, **kwargs):
        vals = {
            "name": name,
            "item_ids": [(0, 0, item) for item in item_val_list],
        }
        return dict(vals, **kwargs)

    @classmethod
    def _remove_extra_keys(cls, price_caches):
        """Remove extra keys that arn't in this module scope."""
        expected_keys = ["discount", "date_start", "id", "date_end", "min_quantity"]
        return [
            {
                key: price_cache[key]
                for key in price_cache.keys()
                if key in expected_keys
            }
            for price_cache in price_caches
        ]
