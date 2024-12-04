# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.rma.models.rma_operation import RmaOperation as RmaOperationBase


class RmaOperation(RmaOperationBase):
    create_inventory_activity_reception = fields.Boolean(
        string="Create Inventory Activity After Reception",
        help="Enable this option to automatically create an activity for inventory "
        "actions required after the reception is processed in an RMA.",
    )
    create_inventory_activity_delivery = fields.Boolean(
        string="Create Inventory Activity After Delivery",
        help="Enable this option to automatically create an activity for inventory "
        "actions required after the delivery is processed in an RMA.",
    )
