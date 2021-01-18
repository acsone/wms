# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv.expression import AND, OR


class RoundInstance(models.Model):

    _inherit = "round.instance"

    @api.model
    def find_bypartner(self, partner):
        """
        Find a delivery_round for this partner according to its position in a delivery template. i.e., in a
        geographic zone
        Round instances are sorted according to the date and the time of
        the picking.

        :param partner:
        :return:
        """
        if not partner:
            # This should not happen unless a picking without partner has been
            # manually created
            return False

        # If delivery address is a contact, take parent
        if partner.type == "contact" and partner.parent_id:
            partner = partner.parent_id

        geo_domain = [("geo_polygon_shape", "geo_contains", partner.geo_point)]
        template_ids = self.env["round.template"].geo_search(geo_domain=geo_domain)

        if template_ids:
            # Look for current itineraries for the partner having a geo_point inside the polygon

            open_itinerary_domain = [
                ("template_id", "in", template_ids),
                ("state", "=", "draft"),
            ]

            itinerary_no_tag_domain = [("tag_ids", "=", False)]
            itinerary_same_partner_tag_domain = [("tag_ids", "in", partner.tag_ids.ids)]
            if partner.tag_ids:
                domain = AND(
                    [
                        open_itinerary_domain,
                        OR(
                            [itinerary_no_tag_domain, itinerary_same_partner_tag_domain]
                        ),
                    ]
                )
            else:
                domain = open_itinerary_domain

            round_instance = self.search(
                domain, order="date ASC, time_picking_planned ASC", limit=1
            )
            if not round_instance:
                return super(RoundInstance, self).find_bypartner(partner)

            return round_instance

        # Keep old way of doing it
        return super(RoundInstance, self).find_bypartner(partner)
