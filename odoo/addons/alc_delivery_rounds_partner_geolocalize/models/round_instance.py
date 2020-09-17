# -*- coding: utf-8 -*-
# Copyright 2002 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class RoundInstance(models.Model):

    _inherit = "round.instance"

    @api.multi
    def _get_partners_to_deliver(self):
        partners_to_deliver = super(RoundInstance, self)._get_partners_to_deliver()
        # Make sure the partners to deliver have coordinates
        for partner in partners_to_deliver:
            # First, try to re compute latitude and longitude if they do not exist
            if not partner.partner_latitude or not partner.partner_longitude:
                partner.geo_localize()
                # Geolocalize has another context : need to force refresh to see the changes in current context
                # Why ???
                partner.refresh()

            # Second : maybe the partner is still not geolocalized because info is missing => raise error
            if not partner.partner_latitude or not partner.partner_longitude:
                raise ValidationError(
                    _("No geolocalization found for partner  %s") % partner.display_name
                )

        return partners_to_deliver
