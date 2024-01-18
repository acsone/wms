from odoo import fields

from odoo.addons.base.models.ir_attachment import IrAttachment as IrAttachmentBase


class IrAttachment(IrAttachmentBase):

    # Gain 1.2 second on record deletion with attachment
    original_id = fields.Many2one[IrAttachmentBase](index=True)
