# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api

from odoo.addons.connector_search_engine.models import se_binding

_logger = logging.getLogger(__name__)


class SeBinding(se_binding.SeBinding):

    @api.model
    def _mark_to_recompute_failed_binding(self):
        """Mark failed binding to recompute."""
        self._flush_search([("state", "=", "recompute_error")])
        self.env.cr.execute(
            """
            UPDATE se_binding
            SET state = 'to_recompute'
            WHERE state = 'recompute_error'
            """
        )
        self.invalidate_model(["state"])
        return self.env.cr.rowcount

    @api.model
    def _ensure_unpublish_inactives(self):
        """Ensure inactive records are unpublished."""
        self._flush_search([("state", "!=", "to_delete")])
        for model, _descr in self._get_indexable_model_selection():
            record_model = self.env[model]
            record_model._flush_search([("active", "=", False)])
            if not hasattr(record_model, "active"):
                continue

            query = self._where_calc([("res_model", "=", model)], active_test=False)
            query.join(
                "se_binding",
                "res_id",
                record_model._table,
                "id",
                "model",
                extra="{rhs}.active = false",
            )
            query_str, params = query.select("se_binding.id")
            self.env.cr.execute(
                f"UPDATE se_binding SET state = 'to_delete' WHERE id IN ({query_str})",
                params,
            )
            _logger.info(
                "Marked %s inactive records of model %s to unpublish",
                self.env.cr.rowcount,
                model,
            )
            self.invalidate_model(["state"])

    @api.model
    def _cron_sanitizer(self):
        """Cron job to sanitize indexes."""
        self._mark_to_recompute_failed_binding()
        self._ensure_unpublish_inactives()
        return True
