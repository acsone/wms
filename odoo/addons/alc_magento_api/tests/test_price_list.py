# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from .common import TestFacadeWithProductFlattenedData


class TestPriceList(TestFacadeWithProductFlattenedData):
    def test_price_list(self):
        router_helper = self.env["alc.eshop.sale_statistics_router.helper"]
        exemple = self._example_product_flattened_data()
        with (
            self.mock_product_data(),
            mock.patch.object(
                router_helper.__class__, "_get_top_ordered"
            ) as mocked_get_top_ordered,
        ):
            mocked_get_top_ordered.side_effect = lambda *args, **kwargs: {
                "data": [{"product_id": exemple["id"], "qty": 1}]
            }
            price_list_facade = self._get_service_facade("price-list")
            result, _error, _location = price_list_facade()
            expeced_result = """<?xml version="1.0" encoding="UTF-8" ?>
                    <price_list>
                        <item>
                            <Article_EN>MATELAS FOAM DOGBED GRIS 120x100cm</Article_EN>
                            <Category_EN>Medical Material / Pets / Dog / Baskets</Category_EN>
                            <Reference>8248538</Reference>
                            <Code_national></Code_national
                            ><TVA>21.0</TVA>
                            <Prix_Vente_Indicatif></Prix_Vente_Indicatif>
                            <ean_13></ean_13>
                            <ext_cti></ext_cti>
                            <Prix_Brut_HTVA_EUR></Prix_Brut_HTVA_EUR>
                            <Prix_Brut_TVAC_EUR></Prix_Brut_TVAC_EUR>
                            <Article_NL>KUSSEN FOAM DOGBED GRIJS 120x100cm</Article_NL>
                            <Category_NL>Medisch materiaal / Huisdieren / Hond / Manden</Category_NL>
                            <Mot_Cle>Matériel Médical / Animaux de compagnie / Chien / Corbeilles</Mot_Cle>
                            <Article>MATELAS FOAM DOGBED GRIS 120x100cm</Article>
                            <Fabricant>KRUUSE *</Fabricant>
                            <url>https://www.alcyonbelux.be/en/p/matelas-foam-dogbed-gris-120x100cm-8248538</url>
                        </item>
                    </price_list>"""
        self.assertXmlEqual(expeced_result, result)
