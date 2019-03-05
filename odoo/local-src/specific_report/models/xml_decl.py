# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class XmlDeclaration(models.TransientModel):
    """
    Intrastat XML Declaration
    """
    _inherit = "l10n_be_intrastat_xml.xml_decl"

    def _build_intrastat_line(self, numlgn, item, linekey, amounts,
                              dispatchmode, extendedmode):
        super(XmlDeclaration, self)._build_intrastat_line(numlgn, item,
                                                          linekey, amounts,
                                                          dispatchmode,
                                                          extendedmode)
        # change precision from 0 decimal to 2
        self._set_Dim(item, 'EXTXVAL', unicode(round(amounts[0], 2)).replace(
            ".", ","))
        self._set_Dim(item, 'EXWEIGHT', unicode(round(amounts[1],
                                                      2)).replace(".", ","))
        self._set_Dim(item, 'EXUNITS', unicode(round(amounts[2], 2)).replace(
            ".", ","))

    @api.multi
    def _get_lines(self, dispatchmode=False, extendedmode=False):
        decl = super(XmlDeclaration, self)._get_lines(dispatchmode,
                                                      extendedmode)
        allclose = decl.findall('.//Data')
        for closetag in allclose:
            closetag.set('close', 'false')
            # set close to false instead of true
        return decl
