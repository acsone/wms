# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo.addons.shipment_advice_planner_toursolver.models.shipment_advice import (
    ShipmentAdvice as Advice,
)


class ShipmentAdvice(Advice):
    def _get_sorted_shipping_ids(self):
        """Return the shippings into the expected delivery order."""
        self.ensure_one()
        return self.loaded_picking_ids.sorted("toursolver_shipment_advice_rank")

    def get_merged_shippings(self, toursolver_resource=None):
        self.ensure_one()

        shippings = self._get_sorted_shipping_ids()
        if toursolver_resource:
            shippings = shippings.filtered(
                lambda p, resource=toursolver_resource: p.toursolver_resource_id
                == resource
            )

        shipping_values = {}
        for shipping in shippings:
            specific_out_locations = defaultdict(list)
            partner_value = shipping_values.get(shipping.partner_id, {})
            number_of_drug = partner_value.get("number_of_drug", 0)
            number_of_drug += shipping.number_of_drug
            item_number_of_drug = partner_value.get("item_number_of_drug", 0)
            item_number_of_drug += shipping.item_number_of_drug

            number_of_cold = partner_value.get("number_of_cold", 0)
            number_of_cold += shipping.number_of_cold
            item_number_of_cold = partner_value.get("item_number_of_cold", 0)
            item_number_of_cold += shipping.item_number_of_cold

            number_of_food = partner_value.get("number_of_food", 0)
            number_of_food += shipping.number_of_food
            item_number_of_food = partner_value.get("item_number_of_food", 0)
            item_number_of_food += shipping.item_number_of_food

            number_of_equipment = partner_value.get("number_of_equipment", 0)
            number_of_equipment += shipping.number_of_equipment
            item_number_of_equipment = partner_value.get("item_number_of_equipment", 0)
            item_number_of_equipment += shipping.item_number_of_equipment

            number_total = partner_value.get("number_total", 0)
            number_total += shipping.number_total
            item_number_total = partner_value.get("item_number_total", 0)
            item_number_total += shipping.item_number_total

            note = partner_value.get("note", "")
            if shipping.partner_id.comment:
                note = shipping.partner_id.comment

            specific_out_locations = self._list_specific_out_locations(
                shipping, partner_value
            )

            partner_value.update(
                {
                    "number_of_drug": number_of_drug,
                    "item_number_of_drug": item_number_of_drug,
                    "number_of_cold": number_of_cold,
                    "item_number_of_cold": item_number_of_cold,
                    "number_of_food": number_of_food,
                    "item_number_of_food": item_number_of_food,
                    "number_of_equipment": number_of_equipment,
                    "item_number_of_equipment": item_number_of_equipment,
                    "number_total": number_total,
                    "item_number_total": item_number_total,
                    "specific_out_locations": specific_out_locations,
                    "note": note,
                    "rank": shipping.rank,
                    "shipping": shipping,
                }
            )
            shipping_values[shipping.partner_id] = partner_value

        result = []
        for partner, _values in shipping_values.items():
            shipping_value = shipping_values.get(partner)
            if not shipping_value:
                continue

            # There is something very stupid in Odoo. If you want to display
            # the address of a partner with the tag <address t-field=.... />
            # you HAVE TO have at least one dot in the t-field
            # (eg: t-field="shipping.partner_id" and not t-field="partner")
            # It's why I append a shipping
            result.append((partner, shipping_value["shipping"], shipping_value))

        return result

    def _list_specific_out_locations(self, shipping, partner_value):
        # Maybe more than one shipping for the customer : complete the out locations
        specific_out_locations = partner_value.get("specific_out_locations", {})
        location_equipment = self.env.ref("__setup__.stock_location_materiel")
        location_cold = self.env.ref("__setup__.stock_location_frigo")
        location_food = self.env.ref("__setup__.stock_location_ali")
        location_med = self.env.ref("__setup__.stock_location_medoc")
        out_locations_med = []
        out_locations_cold = []
        out_locations_food = []
        out_locations_equipment = []

        for move_line in shipping.move_line_ids:
            locations = move_line.mapped("product_id.location_id")
            for location in locations:
                if location == location_med and (
                    shipping.number_of_drug or shipping.item_number_of_drug
                ):
                    out_locations_med.append(move_line.from_loc)
                if location == location_cold and (
                    shipping.number_of_cold or shipping.item_number_of_cold
                ):
                    out_locations_cold.append(move_line.from_loc)
                if location == location_food and (
                    shipping.number_of_food or shipping.item_number_of_food
                ):
                    # We kept internal packages or not
                    if move_line.package_id and move_line.package_id.is_internal:
                        out_locations_food.append(move_line.package_id.name)
                    else:
                        out_locations_food.append(move_line.from_loc)
                if location == location_equipment and (
                    shipping.number_of_equipment or shipping.item_number_of_equipment
                ):
                    # We kept internal packages or not
                    if move_line.package_id and move_line.package_id.is_internal:
                        out_locations_equipment.append(move_line.package_id.name)
                    else:
                        out_locations_equipment.append(move_line.from_loc)

        # Create or update specific_out_locations on the partner
        return self._create_or_update_specific_out_locations_dict(
            specific_out_locations,
            out_locations_med,
            out_locations_food,
            out_locations_cold,
            out_locations_equipment,
        )

    def _create_or_update_specific_out_locations_dict(
        self,
        specific_out_locations,
        out_locations_med,
        out_locations_food,
        out_locations_cold,
        out_locations_equipment,
    ):
        if "med_out_locations" in specific_out_locations.keys():
            new_out_locations = list(
                set(
                    specific_out_locations["med_out_locations"]
                    + list(set(out_locations_med))
                )
            )
            specific_out_locations["med_out_locations"] = new_out_locations
        else:
            specific_out_locations["med_out_locations"] = list(set(out_locations_med))

        if "cold_out_locations" in specific_out_locations.keys():
            new_out_locations = list(
                set(
                    specific_out_locations["cold_out_locations"]
                    + list(set(out_locations_cold))
                )
            )
            specific_out_locations["cold_out_locations"] = new_out_locations
        else:
            specific_out_locations["cold_out_locations"] = list(set(out_locations_cold))

        if "food_out_locations" in specific_out_locations.keys():
            new_out_locations = list(
                set(
                    specific_out_locations["food_out_locations"]
                    + list(set(out_locations_food))
                )
            )
            specific_out_locations["food_out_locations"] = new_out_locations
        else:
            specific_out_locations["food_out_locations"] = list(set(out_locations_food))

        if "equipment_out_locations" in specific_out_locations.keys():
            new_out_locations = list(
                set(
                    specific_out_locations["equipment_out_locations"]
                    + list(set(out_locations_equipment))
                )
            )
            specific_out_locations["equipment_out_locations"] = new_out_locations
        else:
            specific_out_locations["equipment_out_locations"] = list(
                set(out_locations_equipment)
            )

        return specific_out_locations
