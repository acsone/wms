# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestPromotedLinks


class TestPromotedLinksFlow(TestPromotedLinks):
    def test_promoted_link(self):
        # given
        vals_link = {
            "right_product_tmpl_id": self.product_promoted.id,
            "left_product_tmpl_id": self.product_promotes.id,
            "type_id": self.link_type.id,
        }
        # when
        self.env["product.template.link"].create(vals_link)
        # then
        expected = self.product_promotes.display_name
        expected_cross = [expected]
        self.assertEqual(self.product_promoted.promotes, "")
        self.assertEqual(self.product_promoted.promoted_by, expected)
        self.assertEqual(self.product_promoted.cross, expected_cross)
        expected_promoted = self.product_promoted.display_name
        self.assertEqual(self.product_promotes.promotes, expected_promoted)
        self.assertEqual(self.product_promotes.promoted_by, "")
        self.assertEqual(self.product_promotes.cross, [])

        # given
        vals_other_promotes = {"name": "P3", "default_code": "C3"}
        other_promotes = self.env["product.template"].create(vals_other_promotes)
        vals_link = {
            "right_product_tmpl_id": self.product_promoted.id,
            "left_product_tmpl_id": other_promotes.id,
            "type_id": self.link_type.id,
        }
        # when
        self.env["product.template.link"].create(vals_link)
        # then
        expected = ",".join((expected, other_promotes.display_name))
        expected_cross += [other_promotes.display_name]
        self.assertEqual(self.product_promoted.promotes, "")
        self.assertEqual(self.product_promoted.promoted_by, expected)
        self.assertEqual(self.product_promoted.cross, expected_cross)
