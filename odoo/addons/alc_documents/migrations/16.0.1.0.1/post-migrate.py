# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import drop_index


def migrate(cr, version):
    drop_index(cr, "alc_document_attachment_id_index", "alc_document")
