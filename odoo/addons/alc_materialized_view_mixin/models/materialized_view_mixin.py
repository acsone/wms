# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models


class MaterializedViewMixin(models.AbstractModel):

    _name = "materialized.view.mixin"
    _description = "Materialized view mixin"
    _auto = False

    @api.model
    def _get_param_name(self):
        return f"{self._table}_refresh_date"

    @api.model
    def get_refresh_date(self):
        return self.env["ir.config_parameter"].sudo().get_param(self._get_param_name())

    @api.model
    def set_refresh_date(self, date=None):
        date = date or fields.Datetime.now()
        param_name = self._get_param_name()
        self.env["ir.config_parameter"].sudo().set_param(param_name, date)

    @api.model
    def set_cron_date(self, date=None):
        date = date or fields.Datetime.now()
        xmlid = f"{self._module}.{self._table}_refresh_materialized_view"
        cron = self.env.ref(xmlid, raise_if_not_found=False)  # doesn't exist at install
        if cron:  # refresh data asap, but not during the upgrade
            cron.nextcall = date

    @api.model
    def refresh_view(self):
        self.env.cr.execute("refresh materialized view %s", (AsIs(self._table),))
        self.set_refresh_date()

    @api.model
    def get_init_query(self):
        raise NotImplementedError

    @api.model
    def get_init_query_args(self):
        return {"table": AsIs(self._table)}

    def init(self):
        super().init()
        if self._abstract:
            return  # called even on abstract models
        query_drop = "DROP MATERIALIZED VIEW IF EXISTS %s CASCADE"
        self.env.cr.execute(query_drop, (AsIs(self._table),))
        self.env.cr.execute(self.get_init_query(), self.get_init_query_args())
        self.set_refresh_date(date=False)
        self.set_cron_date()
