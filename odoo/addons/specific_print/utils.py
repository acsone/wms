# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def hw_print(model, report_xmlid, printer_id=False, qty=1, **extra):
    document = model.env["report"]._get_raw(model._ids, report_xmlid, qty=qty, **extra)
    report = model.env.ref(report_xmlid)
    behaviour = report.behaviour()[report.id]
    printer = False
    if printer_id:
        printer = model.env["printing.printer"].browse(printer_id)
    if not printer:
        printer = behaviour["printer"]
    if not printer:
        raise UserError(_("No printer assigned"))
    try:
        printer.print_document(report, document, "text")
    except UnicodeEncodeError:
        raise
    except Exception as e:
        _logger.exception("Printer unavailable")
        raise UserError(_("Printer unavailable : %s") % str(e))
