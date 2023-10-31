# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved xml_id from specific_data
    xml_ids = [
        "alc_eshop_form_public_contact",
        "alc_eshop_form_public_registration",
        "alc_eshop_form_authenticated_contact",
        "alc_eshop_form_authenticated_sav",
        "alc_eshop_form_authenticated_rma",
        "alc_eshop_form_authenticated_pvi_labels",
        "alc_eshop_form_authenticated_update_address",
        "alc_eshop_form_authenticated_opinion",
    ]

    openupgrade.rename_xmlids(
        cr,
        [
            (f"alc_eshop_form.{xml_id}", f"alc_eshop_api_forms.{xml_id}")
            for xml_id in xml_ids
        ],
    )
