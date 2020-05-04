# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from contextlib import contextmanager

from odoo import _, api, exceptions, fields, models


class ESBBackend(models.Model):
    _name = "esb.backend"
    _description = "ESB Backend"
    _inherit = "connector.backend"

    sftp_host = fields.Char(string="SFTP Host", compute="_compute_from_env")
    sftp_port = fields.Integer(string="SFTP Port", compute="_compute_from_env")
    sftp_user = fields.Char(string="SFTP User", compute="_compute_from_env")
    sftp_path = fields.Char(string="SFTP Path", compute="_compute_from_env")
    ws_url = fields.Char(string="Web Service Base URL", compute="_compute_from_env")
    ws_user = fields.Char(string="Web Service User", compute="_compute_from_env")
    ws_pwd = fields.Char(string="Web Service password", compute="_compute_from_env")
    timestamp_ids = fields.One2many(
        comodel_name="esb.backend.timestamp",
        inverse_name="backend_id",
        string="Synchronizations",
    )

    @contextmanager
    def work_on(self, model_name, timestamp=None, **kwargs):
        _super = super(ESBBackend, self)
        with _super.work_on(model_name, timestamp=timestamp, **kwargs) as work:
            yield work

    @api.depends()
    def _compute_from_env(self):
        for record in self:
            record.sftp_host = os.getenv("ODOO_ESB_SFTP_HOST", "")
            record.sftp_port = int(os.getenv("ODOO_ESB_SFTP_PORT", 22))
            record.sftp_user = os.getenv("ODOO_ESB_SFTP_USER", "")
            record.sftp_path = os.getenv("ODOO_ESB_SFTP_PATH", "")
            record.ws_user = os.getenv("ODOO_ESB_WS_USER", "")
            record.ws_pwd = os.getenv("ODOO_ESB_WS_PWD", "")
            record.ws_url = os.getenv("ODOO_ESB_WS_BASE_URL", "")

    @api.model
    def get_singleton(self):
        return self.env.ref("connector_esb.esb_backend_config")

    @api.model
    def create(self, vals):
        existing = self.search([])
        if existing:
            raise exceptions.UserError(_("Only 1 ESB configuration is allowed."))
        return super(ESBBackend, self).create(vals)

    def _get_timestamp(self, model, kind=None):
        return self.env["esb.backend.timestamp"].search(
            [("backend_id", "=", self.id), ("model", "=", model), ("kind", "=", kind)]
        )

    @api.model
    def cron_export_product(self):
        backend = self.get_singleton()
        backend._get_timestamp("product.product", "product").export()

    @api.model
    def cron_export_pharmacy(self):
        backend = self.get_singleton()
        backend._get_timestamp("res.partner", kind="pharmacy").export()

    @api.model
    def cron_export_stock(self):
        backend = self.get_singleton()
        backend._get_timestamp("product.product", "stock").export()

    @api.model
    def cron_export_customer(self):
        backend = self.get_singleton()
        backend._get_timestamp("res.partner", "customer").export()

    @api.model
    def cron_export_customer_address(self):
        backend = self.get_singleton()
        backend._get_timestamp("res.partner", "customer.address").export()

    @api.model
    def cron_export_promotion_alcyon(self):
        backend = self.get_singleton()
        backend._get_timestamp("product.pricelist.item", "promotion.alcyon").export()

    @api.model
    def cron_export_product_price(self):
        backend = self.get_singleton()
        exporter = backend._get_timestamp("product.product", "product.price")
        exporter.export()

    @api.model
    def cron_export_special_promotion(self):
        backend = self.get_singleton()
        backend._get_timestamp(
            "product.supplierinfo.esbflux", "special.promotion"
        ).export()

    @api.model
    def cron_export_buy_x_get_y(self):
        backend = self.get_singleton()
        backend._get_timestamp("product.supplierinfo.esbflux", "buyx.gety").export()

    @api.model
    def cron_export_stock_update(self):
        backend = self.get_singleton()
        exporter = backend._get_timestamp("product.product", "stock.update")
        exporter.export()

    @api.model
    def cron_export_document_zip(self):
        backend = self.get_singleton()
        exporter = backend._get_timestamp("ir.attachment", "documents")
        exporter.export()
