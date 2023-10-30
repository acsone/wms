# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    data = [
        ("alc_elasticsearch_security.role_guest", "alc_elasticsearch_role.role_guest"),
        ("alc_elasticsearch_security.role_misc", "alc_elasticsearch_role.role_misc"),
        (
            "alc_elasticsearch_security.role_student_like",
            "alc_elasticsearch_role.role_student_like",
        ),
        (
            "alc_elasticsearch_security.role_food_only",
            "alc_elasticsearch_role.role_food_only",
        ),
        (
            "alc_elasticsearch_security.role_equipment_only",
            "alc_elasticsearch_role.role_equipment_only",
        ),
        (
            "alc_elasticsearch_security.role_veterinary",
            "alc_elasticsearch_role.role_veterinary",
        ),
        (
            "alc_elasticsearch_security.role_wholesaler_veterinary",
            "alc_elasticsearch_role.role_wholesaler_veterinary",
        ),
        (
            "alc_elasticsearch_security.role_wholesaler_pharmacy",
            "alc_elasticsearch_role.role_wholesaler_pharmacy",
        ),
        (
            "alc_elasticsearch_security.role_export_customer",
            "alc_elasticsearch_role.role_export_customer",
        ),
        (
            "alc_elasticsearch_security.role_export_meds",
            "alc_elasticsearch_role.role_export_meds",
        ),
        (
            "alc_elasticsearch_security.role_shareholder",
            "alc_elasticsearch_role.role_shareholder",
        ),
        (
            "alc_elasticsearch_security.role_supplier",
            "alc_elasticsearch_role.role_supplier",
        ),
        (
            "alc_elasticsearch_security.role_supplier_promotion",
            "alc_elasticsearch_role.role_supplier_promotion",
        ),
        (
            "alc_elasticsearch_security.role_is_alcyonnaire",
            "alc_elasticsearch_role.role_is_alcyonnaire",
        ),
        (
            "alc_elasticsearch_security.role_is_alcyonnaire_under_contract",
            "alc_elasticsearch_role.role_is_alcyonnaire_under_contract",
        ),
        (
            "alc_elasticsearch_security.role_non_alcyonnaire",
            "alc_elasticsearch_role.role_non_alcyonnaire",
        ),
    ]
    openupgrade.rename_xmlids(env.cr, data, allow_merge=True)
