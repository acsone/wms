# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake
from odoo.addons.extendable.tests.common import ExtendableMixin


class TestEshopSearchEngineLoyalty(TestBindingIndexBaseFake, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "Loyalty Program Index",
            "backend_id": backend.id,
            "model_id": cls.env.ref("loyalty.model_loyalty_program").id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "serializer_type": "loyalty_program",
        }

    @classmethod
    def setup_records(cls, backend=None):
        cls.LoyaltyProgram = cls.env["loyalty.program"]
        backend = backend or cls.backend
        # ensure we only work with the index we'll create
        cls.se_index_model.search([]).unlink()
        # ensuire all loyalty programs are unpublished
        cls.LoyaltyProgram.search([]).active = False
        # create an index for partner model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        date_start = cls._get_date()
        date_end = cls._get_date(day_offset=1)
        cls.loyalty_program = cls.env["loyalty.program"].create(
            {
                "name": "test program",
                "date_from": date_start,
                "date_to": date_end,
                "active": True,
            }
        )
        cls.rule = cls.env["loyalty.rule"].create(
            {"name": "test rule", "sequence": 1.0, "program_id": cls.loyalty_program.id}
        )
        cls.all_loyalty_programs = cls.LoyaltyProgram.search([])
        cls.all_loyalty_programs.action_toggle_is_published()
        cls.all_loyalty_programs._compute_binding_ids()

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    @classmethod
    def _expected_result(cls, loyalty_program):
        return {
            "id": loyalty_program.id,
            "name": loyalty_program.name,
            "date_start": loyalty_program.date_start.isoformat(),
            "date_end": loyalty_program.date_end.isoformat(),
            "type": "promotion",
            "sequence": loyalty_program.sequence,
            "time_frame": {
                "gte": loyalty_program.date_start.isoformat(),
                "lte": loyalty_program.date_end.isoformat(),
            },
            "rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "sequence": rule.sequence,
                    "program_id": loyalty_program.id,
                }
                for rule in loyalty_program.rule_ids
            ],
        }

    def test_serializer(self):
        """Test the serializer of loyalty program."""
        self.assertEqual(
            self.se_index._get_serializer().serialize(self.loyalty_program),
            self._expected_result(self.loyalty_program),
        )

    def test_00(self):
        """Cron will export all new published banners."""
        self.backend.cron_synchronize_loyalty_programs()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 1)
            program_info = index_call.get("args")[0]
            self.assertDictEqual(
                program_info, self._expected_result(self.loyalty_program)
            )
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")

    def test_01(self):
        """Loyalty Program unchanged shouldn't be exported."""
        self.test_00()
        self.loyalty_program.action_synchronize_records()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")

    def test_02(self):
        """Loyalty Program changed should be exported."""
        self.test_00()
        self.loyalty_program.name = "new name"
        self.loyalty_program.action_synchronize_records()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            program_info = index_call.get("args")[0]
            self.assertDictEqual(
                program_info, self._expected_result(self.loyalty_program)
            )
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")

    def test_03(self):
        """The cron should export only the changed banner."""
        self.test_00()
        self.loyalty_program.name = "new name"
        self.backend.cron_synchronize_loyalty_programs()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 1)
            program_info = index_call.get("args")[0]
            self.assertDictEqual(
                program_info, self._expected_result(self.loyalty_program)
            )
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")

    def test_04(self):
        """Unpublished Loyalty Program should be deleted."""
        self.test_00()
        self.loyalty_program.action_toggle_is_published()
        self.assertFalse(self.loyalty_program.is_published)
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_delete")

    def test_05(self):
        """Future Loyalty Program should be published."""
        self.test_00()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")
        self.loyalty_program.write(
            {
                "date_start": self._get_date(day_offset=10),
                "date_end": self._get_date(day_offset=15),
            }
        )
        self.backend.cron_synchronize_loyalty_programs()
        self.assertTrue(self.loyalty_program.is_published)
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_export")

    def test_06(self):
        """Past Loyalty Program should be deleted."""
        self.test_00()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")
        self.loyalty_program.write(
            {
                "date_start": self._get_date(day_offset=-15),
                "date_end": self._get_date(day_offset=-10),
            }
        )
        self.backend.cron_synchronize_loyalty_programs()
        self.assertFalse(self.loyalty_program.is_published)
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_delete")

    def test_07(self):
        """Loyalty Program set to be recomputed after edit."""
        self.test_00()
        self.loyalty_program.name = "new name"
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_recompute")

    def test_08(self):
        """Loyalty Program set to be recomputed after unlink of rules."""
        self.test_00()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")
        self.rule.unlink()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_recompute")

    def test_09(self):
        """Loyalty Program set to be recomputed after un update of a rule."""
        self.test_00()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")
        self.rule.write({"sequence": 10})
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_recompute")

    def test_10(self):
        """Loyalty program is set to be recomputed after the addition of a rule."""
        self.test_00()
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "done")
        self.env["loyalty.rule"].create(
            {
                "name": "test rule",
                "sequence": 1.0,
                "program_id": self.loyalty_program.id,
            }
        )
        self.assertEqual(self.loyalty_program.se_binding_ids.state, "to_recompute")
