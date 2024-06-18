# Copyright 2022 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestESRolesVTGroups


class TestESRolesVTGroupsFlow(TestESRolesVTGroups):
    def test_partner_role(self):
        # given
        vals_partner = {
            "name": "P",
            "partner_type": "guest",
            "veterinary_group_ids": [(6, 0, self.vt_group.ids)],
        }
        # when
        partner = self.env["res.partner"].create(vals_partner)
        # then
        vt_role = self.vt_group._get_role_name()
        price_list = self.env.ref("product.list0")
        price_role_name = price_list._get_role_name()
        expected = {"guest", price_role_name, vt_role, "non_alcyonnaire"}
        self.assertEqual(set(partner.elasticsearch_role.split(",")), expected)
