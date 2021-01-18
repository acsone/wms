# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    picking_zone_id = fields.Many2one("picking.zone", string="Picking zone")
    zone = fields.Char("Zone")
    corridor = fields.Char("Corridor")
    shelf = fields.Char("Shelf")
    height = fields.Char("Height")
    box = fields.Char("Box")
    is_valid_location = fields.Boolean(
        "Valid location",
        compute="_compute_is_valid_location",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "unique_location_coordinates",
            "UNIQUE(zone, corridor, shelf, height, box)",
            _("The location coordinate must be unique"),
        )
    ]

    @api.multi
    @api.depends("zone", "corridor", "shelf", "height", "box")
    def _compute_is_valid_location(self):
        for location in self:
            if (
                not location.zone
                or not location.corridor
                or not location.shelf
                or not location.height
                or not location.box
            ):
                location.is_valid_location = False
            else:
                location.is_valid_location = True
                location.name = u"{}{}{}{}{}".format(
                    location.zone,
                    location.corridor,
                    location.shelf,
                    location.height,
                    location.box,
                )

    @api.multi
    def name_get(self):
        """ Redefined from standard Odoo !

        By default when a location as the usage field set as 'view' its name
        is not computed with its parents location.
        Here we want the same to happen when a location as the flag
        'act_as_view' set.

        """
        ret_list = []
        for location in self:
            orig_location = location
            name = location.name
            # Chanded from default implementation
            # while location.location_id and location.usage != 'view':
            while (
                location.location_id
                and location.usage != "view"
                and not location.act_as_view
            ):
                location = location.location_id
                name = location.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

    def generate_checksum(self):
        for location in self:
            if (
                location.bin_checksum_1 is not False
                and not location.is_checksum_invalid
            ):
                continue
            # if location.bin_checksum_1 not in (False, '00', '12'):
            #    # Checksum already exists, skip
            #    continue
            old_checksum = location.bin_checksum_1

            checksum_not_available = location._calculate_unavailable_checksum(
                strict=True
            )

            formated_checksum = ["{:02d}".format(i) for i in range(100)]
            picklist = list(set(formated_checksum) - set(checksum_not_available))
            if not picklist:
                raise UserError(
                    _("There is no checksum available for location %s") % location.name
                )

            # Assign checksum
            checksum = random.choice(picklist)
            location.bin_checksum_1 = checksum

            # location.bin_checksum_2 = checksum
            location.bin_checksum_3 = "GEN"
            location.is_checksum_invalid = False

            self.filtered(
                lambda r, chk=old_checksum: r.bin_checksum_1 == chk
                and r.is_checksum_invalid
            ).check_checksum_valid()

    @api.multi
    def _calculate_unavailable_checksum(self, strict=False):
        """
        Compute a 2 digits checksum. Rules:
        - Cannot be 00, 12
        - Cannot already exist on the shelf + shelf left/right
        """
        self.ensure_one()
        location = self
        if not location.is_valid_location:
            return None

        shelf = location.shelf

        checksum_not_available = {"00", "12"}

        try:
            shelf_code = int(shelf)
            is_letter = False
        except ValueError:
            shelf_code = ord(shelf)
            is_letter = True

        def convert(code):
            if is_letter:
                if code < ord("A") or code > ord("Z"):
                    return None
                code = chr(code)
            else:
                if code < 1 or code > 99:
                    return None
                code = "{:02d}".format(code)
            return code

        query_or = []
        query_args = {
            "id": location.id,
            "zone": location.zone,
            "corridor": location.corridor,
            "shelf": location.shelf,
            "height": location.height,
            "box": location.box,
        }
        # Get checksums of this shelf
        query_or.append(
            """ (
            zone = %(zone)s
            AND corridor = %(corridor)s
            AND shelf = %(shelf)s
            ) """
        )
        # Get checksums of left/right/opposite shelfs, same height
        query_or.append(
            """ (
            zone = %(zone)s
            AND corridor = %(corridor)s
            AND shelf IN %(next_shelfs)s
            AND height = %(height)s
            ) """
        )
        query_args["next_shelfs"] = tuple(
            filter(
                None,
                map(convert, (shelf_code - 2, shelf_code + 2, (shelf_code % 2 or -1))),
            )
        )
        # Get checksums of other corridors, same location
        query_or.append(
            """ (
            zone = %(zone)s
            AND shelf = %(shelf)s
            AND height = %(height)s
            AND box = %(box)s
            ) """
        )
        # Get checksums of other shelfs, same location
        query_or.append(
            """ (
            zone = %(zone)s
            AND corridor = %(corridor)s
            AND height = %(height)s
            AND box = %(box)s
            ) """
        )
        # Build query
        query = """
            SELECT DISTINCT bin_checksum_1
            FROM stock_location
            WHERE active AND id!=%(id)s
            """
        if strict:
            # For Aliment: add
            #   AND height in ('A', 'B')
            query += """
            -- AND height in ('A', 'B')
            -- AND corridor in ('A', 'B', 'C', 'D', 'E')
            """
        query += (
            """
            AND (
            """
            + " OR ".join(query_or)
            + ")"
        )
        self.env.cr.execute(query, query_args)

        checksum_not_available |= {x[0] for x in self.env.cr.fetchall()}

        return checksum_not_available

    @api.multi
    def check_checksum_valid(self):
        for location in self:
            if not location.is_valid_location:
                continue
            if not location.bin_checksum_1:
                continue
            blocked = location._calculate_unavailable_checksum()
            if location.bin_checksum_1 in blocked:
                location.is_checksum_invalid = True
            else:
                location.is_checksum_invalid = False

    is_checksum_invalid = fields.Boolean("Invalid Checksum")
