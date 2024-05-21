# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestFacadePickings


class TestPackingSlip(TestFacadePickings):
    def test_packing_slip(self):
        packing_slip_facade = self._get_service_facade("packing-slip")
        result, _error, _location = packing_slip_facade(date="1900-01-01")
        self.maxDiff = None
        expeced_result = f"""<?xml version="1.0" encoding="UTF-8" ?>
            <packing_slip>
                <note>
                    <ne_id>{self.picking_done.id}</ne_id>
                    <date>{self.picking_done.date.date()}</date>
                    <items>
                        <item>
                            <qty>1.0</qty>
                            <reference>SHP</reference>
                            <article>Shipit</article>
                            <tva></tva>
                            <name>Shipit</name>
                            <numero_de_suite></numero_de_suite>
                            <lot></lot>
                            <peremption></peremption>
                            <prix_net_htva>0.0</prix_net_htva>
                            <prix_brut_htva>0.0</prix_brut_htva>
                        </item>
                    </items>
                        <name>Partner</name>
                        <email></email>
                        <address></address>
                        <locality></locality>
                        <country>Belgique</country>
                </note>
                <note>
                    <ne_id>{self.picking_half.id}</ne_id>
                    <date>{self.picking_half.date.date()}</date>
                    <items>
                        <item>
                            <qty>1.0</qty>
                            <reference>SHP</reference>
                            <article>Shipit</article>
                            <tva></tva>
                            <name>Shipit</name>
                            <numero_de_suite></numero_de_suite>
                            <lot></lot>
                            <peremption></peremption>
                            <prix_net_htva>0.0</prix_net_htva>
                            <prix_brut_htva>0.0</prix_brut_htva>
                        </item>
                    </items>
                    <name>Partner</name>
                    <email></email>
                    <address></address>
                    <locality></locality>
                    <country>Belgique</country>
                </note>
            </packing_slip>"""
        self.assertXmlEqual(expeced_result, result)
