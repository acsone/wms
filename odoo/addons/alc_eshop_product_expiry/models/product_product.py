# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.queue_job.job import job


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    @job(default_channel="root.search_engine.synchronize_stock")
    def synchronize_all_binding_stock_level(self, company_id=None):
        # Use `sudo` because this action might be triggered
        # from a low access level user (eg: external user on portal/website).
        # In any case, the real operation is done w/ the backend user below.

        # ensure user company propagation if the method has been delayed...
        # this feature should be provided by queue job ...
        res = super(ProductProduct, self).synchronize_all_binding_stock_level(
            company_id=company_id
        )
        # At the same time we check for the stock, we also check for the expiry date
        # aka best_before_date
        products = self
        if company_id:
            products = self.with_context(force_company=company_id.id)
        all_bindings = products.mapped("shopinvader_bind_ids")
        backends = all_bindings.mapped("backend_id")
        # ensure to invalidate cache since the date should be modified by an other move
        # into the same running process
        products.invalidate_cache(["best_before_date", "older_lot_id"], products.ids)
        all_bindings.invalidate_cache(
            ["best_before_date", "older_lot_id"], all_bindings.ids
        )
        for backend in backends:
            bindings = all_bindings.filtered(lambda r, b=backend: r.backend_id == b)
            # To avoid access rights issues, execute the job with sudo
            bindings = bindings.sudo()
            for binding in bindings:
                if binding.sync_state == "new":
                    # this binding have been not yet computed
                    # so we do not care to update it as it's not yet
                    # on the site. The right stock qty will be exported
                    # at it's first export
                    continue
                data = binding.data
                best_before_date = data.get("best_before_date")
                if best_before_date != binding.best_before_date:
                    data["best_before_date"] = binding.best_before_date
                    vals = {"data": data}
                    if binding.backend_id.synchronize_stock == "immediatly":
                        binding.write(vals)
                        binding.synchronize()
                    elif binding.backend_id.synchronize_stock == "in_batch":
                        if binding.sync_state == "done":
                            vals["sync_state"] = "to_update"
                        binding.write(vals)
        return res
