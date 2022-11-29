# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


class TestImport:
    @classmethod
    def _create_external_id(cls, record):
        vals = {
            "model": record._name,
            "module": "external_id",
            "res_id": record.id,
            "name": ":".join((record._name.replace(".", "_"), str(record.id))),
        }
        external_id = cls.env["ir.model.data"].create(vals)
        return external_id.complete_name
