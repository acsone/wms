# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.model
    def create(self, vals):
        """Update the model product.supplierinfo.esbflux"""
        rec = super(ProductSupplierInfo, self).create(vals)
        if rec._is_promotion_buyx_gety():
            rec._update_flux('create', 'buyxgety')
        if rec._is_promotion_special():
            rec._update_flux('create', 'specialpromotion')
        return rec

    @api.multi
    def unlink(self):
        """Update the model product.supplierinfo.esbflux"""
        for record in self:
            if record._is_promotion_buyx_gety():
                record._update_flux('delete', 'buyxgety')
            if record._is_promotion_special():
                record._update_flux('delete', 'specialpromotion')
        return super(ProductSupplierInfo, self).unlink()

    @api.multi
    def write(self, vals):
        """Update the flux esb.

        If the write modify values that impact a promotion that
        is send through the connector (buyx_gety or special_promotion)
        Then add corresponding actions to be send.
        """
        updating_buyx_gety = self._is_modifying_buyx_gety_promotion(vals)
        if updating_buyx_gety:
            for record in self:
                if record._is_promotion_buyx_gety():
                    record._update_flux('delete', 'buyxgety')
        updating_special = self._is_modifying_special_promotion(vals)
        if updating_special:
            for record in self:
                if record._is_promotion_special():
                    record._update_flux('delete', 'specialpromotion')

        res = super(ProductSupplierInfo, self).write(vals)

        if updating_buyx_gety or updating_special:
            for record in self:
                if record._is_promotion_buyx_gety():
                    record._update_flux('create', 'buyxgety')
                if record._is_promotion_special():
                    record._update_flux('create', 'specialpromotion')

        return res

    @api.multi
    def _is_promotion_buyx_gety(self):
        """Is it a valid promotion buyx gety."""
        self.ensure_one()
        return (
            self.ratio_main_product
            and self.ratio_promotional_product
            and self.date_start
            and self.date_end
        )

    @api.multi
    def _is_promotion_special(self):
        """Is it a valid special promotion"""
        self.ensure_one()
        return self.discount_sale and self.date_start and self.date_end

    @api.model
    def _is_modifying_buyx_gety_promotion(self, vals):
        """Is one of the field of the promotion being modified."""
        impacting_fields = {
            'ratio_main_product',
            'ratio_promotional_product',
            'date_start',
            'date_end',
        }
        return len(impacting_fields & set(vals.keys()))

    @api.model
    def _is_modifying_special_promotion(self, vals):
        """Is one of the field of special promotion being modified."""
        impacting_fields = {'discount_sale', 'date_start', 'date_end'}
        return len(impacting_fields & set(vals.keys()))

    @api.multi
    def _update_flux(self, action, flux):
        """Add in esb flux an entry for this action on the record."""
        self.ensure_one()
        values = {
            'ratio_main_product': self.ratio_main_product,
            'ratio_promotional_product': self.ratio_promotional_product,
            'discount_sale': self.discount_sale,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'product_tmpl_id': self.product_tmpl_id.id,
            'action': action,
            'flux': flux,
            'real_id': self.id,
        }
        self.env['product.supplierinfo.esbflux'].sudo().create(values)
        return
