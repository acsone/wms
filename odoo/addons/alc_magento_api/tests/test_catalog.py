# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestFacadeWithProductFlattenedData


class TestCatalog(TestFacadeWithProductFlattenedData):
    def test_catalog(self):
        expected = """<?xml version="1.0" encoding="UTF-8" ?>
            <catalog>
                <item>
                    <Article_NL>KUSSEN FOAM DOGBED GRIJS 120x100cm</Article_NL>
                    <Reference>8248538</Reference>
                    <Prix_Brut_TVAC_EUR></Prix_Brut_TVAC_EUR>
                    <url>https://www.alcyonbelux.be/fr/p/matelas-foam-dogbed-gris-120x100cm-8248538</url>
                    <Prix_Vente_Indicatif></Prix_Vente_Indicatif>
                    <Mot_Cle>Matériel Médical / Animaux de compagnie / Chien / Corbeilles</Mot_Cle>
                    <ean_13></ean_13>
                    <Prix_Brut_HTVA_EUR></Prix_Brut_HTVA_EUR>
                    <ext_cti></ext_cti>
                    <Category_EN>Medical Material / Pets / Dog / Baskets</Category_EN>
                    <Category_NL>Medisch materiaal / Huisdieren / Hond / Manden</Category_NL>
                    <Article>MATELAS FOAM DOGBED GRIS 120x100cm</Article>
                    <Article_EN>MATELAS FOAM DOGBED GRIS 120x100cm</Article_EN>
                    <Fabricant>KRUUSE *</Fabricant>
                    <TVA>21.0</TVA>
                    <Code_national></Code_national>
                </item>
            </catalog>"""
        product_facade = self._get_service_facade("catalog")
        with self.mock_product_data():
            result, error, location = product_facade(language="FR")
        self.assertEqual(error, [])
        self.assertEqual(location, None)
        self.assertXmlEqual(result, expected)

    def test_catalog_supplier_promotion(self):
        product_facade = self._get_service_facade("catalog")
        self.partner.partner_type = "guest"
        self.partner.supplier_promotion_sale_allowed = True
        flattened_data = self._example_product_flattened_data()
        flattened_data["has_supplier_promotion"] = True
        flattened_data["supplier_promotion_only_for_veterinaries"] = False
        return_value = (r for r in [self._wrap_flattened_data(flattened_data)])
        with self.mock_product_data(return_value=return_value):
            result, _, _ = product_facade(language="FR")
            self.assertIn("FREE products", result)
        flattened_data["supplier_promotion_only_for_veterinaries"] = True
        return_value = (r for r in [self._wrap_flattened_data(flattened_data)])
        with self.mock_product_data(return_value=return_value):
            result, _, _ = product_facade(language="FR")
            self.assertNotIn("FREE products", result)
        self.partner.partner_type = "veterinary"
        return_value = (r for r in [self._wrap_flattened_data(flattened_data)])
        with self.mock_product_data(return_value=return_value):
            result, _, _ = product_facade(language="FR")
            self.assertIn("FREE products", result)

    def test_catalog_supplier_discount(self):
        product_facade = self._get_service_facade("catalog")
        self.partner.partner_type = "guest"
        self.partner.supplier_promotion_sale_allowed = True
        flattened_data = self._example_product_flattened_data()
        flattened_data["supplier_discount_only_for_veterinaries"] = False
        flattened_data["supplier_discount_discount_sale"] = "10%"
        return_value = (r for r in [self._wrap_flattened_data(flattened_data)])
        with self.mock_product_data(return_value=return_value):
            result, _, _ = product_facade(language="FR")
            self.assertIn("10%", result)
        flattened_data["supplier_discount_only_for_veterinaries"] = True
        return_value = (r for r in [self._wrap_flattened_data(flattened_data)])
        with self.mock_product_data(return_value=return_value):
            result, _, _ = product_facade(language="FR")
            self.assertNotIn("10%", result)
        self.partner.partner_type = "veterinary"
        return_value = (r for r in [self._wrap_flattened_data(flattened_data)])
        with self.mock_product_data(return_value=return_value):
            result, _, _ = product_facade(language="FR")
            self.assertIn("10%", result)
