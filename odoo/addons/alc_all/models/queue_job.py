from odoo import fields

from odoo.addons.base.models.ir_attachment import IrAttachment as IrAttachmentBase
from odoo.addons.queue_job.models.queue_job import QueueJob as QueueJobBase


class QueueJob(QueueJobBase):

    # Gain 4 seconds
    message_main_attachment_id = fields.Many2one[IrAttachmentBase](index=True)
