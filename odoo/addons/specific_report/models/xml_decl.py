# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class XmlDeclaration(models.TransientModel):
    """
    Intrastat XML Declaration
    """

    _inherit = "l10n_be_intrastat_xml.xml_decl"

    def _update_Dim(self, item, prop, value):
        dim = item.find(".//Dim[@prop='%s']" % prop)
        if dim is not None:
            dim.text = value

    def _build_intrastat_line(
        self, numlgn, item, linekey, amounts, dispatchmode, extendedmode
    ):
        super(XmlDeclaration, self)._build_intrastat_line(
            numlgn, item, linekey, amounts, dispatchmode, extendedmode
        )
        if dispatchmode:
            self._update_Dim(item, "EXTRF", "29")
        else:
            self._update_Dim(item, "EXTRF", "19")
        # change precision from 0 decimal to 2
        self._update_Dim(item, "EXTXVAL", unicode(round(amounts[0], 2)))
        # if 0.0 is forbid by onegate, must be set to 0.01
        weight = amounts[1]
        if weight < 0.01:
            weight = 0.01
        self._update_Dim(item, "EXWEIGHT", unicode(round(weight, 2)))
        self._update_Dim(item, "EXUNITS", unicode(round(amounts[2], 2)))

    @api.multi
    def _get_lines(self, dispatchmode=False, extendedmode=False):
        decl = super(XmlDeclaration, self)._get_lines(dispatchmode, extendedmode)
        allclose = decl.findall(".//Data")
        for closetag in allclose:
            closetag.set("close", "false")
            # set close to false instead of true
        return decl
