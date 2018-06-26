# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from . import mappings
from .common import (
    convert_product_id,
    create_or_update,
)


def convert_stage(value):
    """ Return stage ref """
    if value == 'C':
        return 'helpdesk.stage_solved'
    return 'helpdesk.stage_in_progress'


class DB2MapperHelpdeskTicket(object):

    @classmethod
    def prepare_ticket_values(cls, rec, row):
        po_name = str(int(row['hpbsui']))
        purchase = rec.env['purchase.order'].search([('name', '=', po_name)])
        if not purchase:
            raise Exception("Purchase %s doesn't exists (yet?)" % po_name)

        # don't import, multiple user are used on AS400 side
        # some are even workstation users thus not accurate
        user_id = False
        stage = rec.env.ref(convert_stage(row['hpssts']))

        # drpprb = code problème
        reason = row['hpbcpb']
        if not reason:
            raise Exception("No problem code, thus no problem?" % po_name)
        reason = rec.env.ref(mappings.ISSUE_CODE[reason])

        # drpart = code article
        product = rec.env.ref(convert_product_id(row['drpart']))

        description = (
            u'[MIGRATION]\n'
            + row['hpbde1'] + u'\n' + row['hpbde2'] + u'\n' + row['hpbde3']
            + u'\n' + row['hpbde4'] + u'\n' + row['hpbde5']
            + u"\n\nCommentaires:\n"
            + row['hpbsco']
        )

        invoice_num = row['hpsnfa']

        # we don't want to generate an invoice for this as it would mean
        # to import another object, thus just provide the reference
        if invoice_num:
            description += u"\n\nNuméro facture: " + invoice_num

        title = '%s-%s-%s' % (po_name, int(row['hpbnli']), int(row['hpbcpb']))
        values = {
            'name': title,
            'user_id': user_id,
            'team_id': rec.env.ref('specific_helpdesk.supplier_team').id,
            'description': description,
            'active': True,
            # 'ticket_type_id', default "Incident"
            'color': 9,
            'kanban_state': 'normal',  # normal, blocked, done
            'partner_id': purchase.partner_id.id,
            'stage_id': stage.id,
            'purchase_order_id': purchase.id,
            'helpdesk_ticket_reason_id': reason.id,
            'product_id': product.id,
        }
        return values

    @classmethod
    def process(cls, rec, db2_table, tmp_id):
        cr = rec.env.cr
        query = (
            "SELECT hp.id, hpbsui, hpbnli, hpbcpb, hpbsco,"
            "       hpbde1, hpbde2, hpbde3, hpbde4, hpbde5,"
            "       drpseq, drpart, drplot,"
            "       hpbsid, hpbsid, hpssts, hpsnfa"
            " FROM db2_hisprb as hp"
            " LEFT JOIN db2_drecep"
            "   ON hpbsui = drpsui AND hpbnli = drpnli AND hpbcpb = drpprb"
            " LEFT JOIN db2_hisspr"
            "   ON hpbsui = hpssui AND hpbnli = hpsnli AND hpbcpb = hpscpb"
            " WHERE hp.id = %s")
        cr.execute(query, [tmp_id])
        row = cr.fetchone()
        if not row:
            raise Exception("Nothing to process")
        row = {c.lower(): row[idx]
               for idx, c in enumerate(
                   [d[0] for d in cr.description]
               )}
        values = cls.prepare_ticket_values(rec, row)

        # transform float and string to int to remove . and spaces
        # while creating xmlid
        xmlid = '__import__.helpdesk_ticket_%s_%s_%s' % (
            int(row['hpbsui']), int(row['hpbnli']), int(row['hpbcpb']))

        ticket_model = rec.env['helpdesk.ticket'].with_context(
            tracking_disable=True,
        )
        new = create_or_update(
            ticket_model, xmlid, values)

        return new
