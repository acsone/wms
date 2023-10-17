# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["attribute.attribute"].search([("attribute_type", "=", "multiselect")]).write(
        {"widget": "many2many_tags"}
    )
    env.ref("alc_pim.attribute_species_ids").write(
        {
            "sequence": 0,
            "attribute_group_id": env.ref(
                "alc_pim_attribute_group.general_attribute_group"
            ).id,
        }
    )
