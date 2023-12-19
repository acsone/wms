# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.stock.models.stock_picking import PickingType
from odoo.addons.stock_picking_batch_creation.wizards import make_picking_batch


class MakePickingBatch(make_picking_batch.MakePickingBatch):

    picking_type_ids = fields.Many2many[PickingType](domain="[('code','=','internal')]")

    _ignored_partner_ids = fields.Many2many[Partner](
        compute="_compute_ignored_partner_ids",
        readonly=False,
        string="Ignored partners",
        store=False,
    )

    def _compute_ignored_partner_ids(self):
        # do nothing
        pass

    def _compute_device_to_use(self, first_picking_to_cluster):
        partner = first_picking_to_cluster.partner_id
        partner_devices = partner._get_specific_stock_devices()
        if partner_devices:
            menu_devices = self.stock_device_type_ids
            for device in partner_devices:
                if device in menu_devices:
                    # Only one device should be put by zone on the partner so creating
                    # a list is useless
                    return device
        return super()._compute_device_to_use(first_picking_to_cluster)

    def _get_picking_domain_for_additional(self):
        domain = super()._get_picking_domain_for_additional()
        if self._ignored_partner_ids:
            domain.append(("partner_id", "not in", self._ignored_partner_ids.ids))
        return domain

    def _get_additional_picking(self):
        additional_picking = super()._get_additional_picking()
        if additional_picking:
            partner = additional_picking.partner_id
            if self._check_current_device_for_partner(partner):
                return additional_picking
            self._ignored_partner_ids |= additional_picking.partner_id
            return self._get_additional_picking()
        return additional_picking

    def _check_current_device_for_partner(self, partner):
        """We check that the current device is compatible with the partner.

        The device is compatible if:
        - the partner has no specific device
        - the partner has specific devices
                      and the current device is one of them
        - the parthner has specific devices
                       and the current device is not one of them
                       and the partner has no device on the menu
        """
        partner_devices = partner._get_specific_stock_devices()
        if not partner_devices:
            # has no specific device
            return True
        # has specific device
        if self._device in partner_devices:
            # the current device is one of the partner devices
            return True
        # the current device is not one of the partner devices
        if not partner_devices & self.stock_device_type_ids:
            # the partner has no device on the menu
            return True
        return False
