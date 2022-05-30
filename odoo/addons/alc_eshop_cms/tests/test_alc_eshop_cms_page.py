# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import SavepointComponentCase

from .common import CommonMixin


class TestAlcEshopPage(SavepointComponentCase, CommonMixin):
    @classmethod
    def setUpClass(cls):
        super(TestAlcEshopPage, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        super(TestAlcEshopPage, cls)._init_langs()
        cls.ir_att_img_xml_id = "alc_eshop_cms.ir_att_img_team_bertrand"
        cls.ir_att_img = cls.env.ref(cls.ir_att_img_xml_id)
        cls.page = cls.env["alc.eshop.cms.page"].create(
            {
                "name": "Test page",
                "lang_ids": [(6, 0, cls.lang_fr.ids)],
                "cms_page_group_id": cls.env.ref(
                    "alc_eshop_cms.alc_eshop_cms_page_group_others"
                ).id,
                "cms_page_slot_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "alc_eshop_cms.alc_eshop_cms_page_slot_footer"
                            ).id
                        ],
                    )
                ],
                "content": cls._gen_content(
                    "/web/image/{}/test.jpg".format(cls.ir_att_img.id),
                    "/web/image/{}/test.jpg".format(cls.ir_att_img_xml_id),
                ),
            }
        )

    @classmethod
    def _gen_content(cls, *image_urls):
        return "<p>Test content</p>" + "".join(
            '<img src="{}" class="test class" width="100%"/>'.format(url)
            for url in image_urls
        )

    def test_get_content_generate_storage_image(self):
        existing_storage_image = self.env["storage.image"].search([])
        json = self.page._to_json()
        self.assertTrue(json)
        new_storage_image = (
            self.env["storage.image"].search([]) - existing_storage_image
        )
        self.assertEqual(len(new_storage_image), 1)
        content = json[0]["data"]["content"]
        self.assertEqual(
            content, self._gen_content(new_storage_image.url, new_storage_image.url)
        )
        existing_storage_image |= new_storage_image
        self.page._to_json()
        new_storage_image = (
            self.env["storage.image"].search([]) - existing_storage_image
        )
        self.assertFalse(new_storage_image)
