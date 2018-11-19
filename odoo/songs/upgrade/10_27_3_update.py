# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def drop_ir_cron_connector_esb_export_documents(ctx):
    rec = ctx.env.ref('connector_esb.ir_cron_esb_export_document_zip',
                      raise_if_not_found=False)
    if rec:
        rec.unlink()


@anthem.log
def pre(ctx):
    """ PRE 10.27.3 """
    drop_ir_cron_connector_esb_export_documents(ctx)
