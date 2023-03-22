# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

IDS = {
    "product_categ_materiel",
    "product_categ_medoc",
    "product_categ_finance",
    "product_categ_vet_belges",
    "product_categ_stupefiant_vet",
    "product_categ_importation",
    "product_categ_humain",
    "product_categ_parapharmacie",
    "product_categ_finance_divers",
    "product_categ_finance_opcli",
    "product_categ_finance_coope",
    "product_categ_antimicrobiens",
    "product_categ_pis",
    "product_categ_oeil_oreille",
    "product_categ_antiparasite",
    "product_categ_sys_nerveux",
    "product_categ_vasculo",
    "product_categ_vitamines",
    "product_categ_vaccins",
    "product_categ_divers_veto",
    "product_categ_hormones",
    "product_categ_psychotropes_25",
    "product_categ_stupefiant",
    "product_categ_topiques",
    "product_categ_phytosanitaires",
    "product_categ_homeo",
    "product_categ_chimiques",
    "product_categ_divers_para",
    "product_categ_ali_comp",
    "product_categ_ali_dietetique",
    "product_categ_ali_physio",
    "product_categ_ali_divers",
    "product_categ_mat_sutures",
    "product_categ_mat_cardio",
    "product_categ_mat_dentisterie",
    "product_categ_mat_equins",
    "product_categ_mat_rurale",
    "product_categ_mat_sav",
    "product_categ_mat_ortho",
    "product_categ_mat_sut_bobine",
    "product_categ_mat_equipement",
    "product_categ_mat_instrumentation",
    "product_categ_mat_img_echo",
    "product_categ_mat_img_radio",
    "product_categ_mat_img_endo",
    "product_categ_mat_occasion",
    "product_categ_mat_conso",
    "product_categ_mat_petshop",
    "product_categ_mat_marge",
    "product_categ_finance_frais",
    "product_categ_finance_remises_fournisseurs",
    "product_categ_finance_divers_divers",
    "product_categ_finance_bonus_actionnaires",
    "product_categ_finance_remises_partenariat",
    "product_categ_finance_remises_geste_commercial",
    "product_categ_finance_cheques_clients",
    "product_categ_finance_divers_service",
    "product_categ_undefined",
    "product_categ_colis_souverain",
}


def pre_init_hook(cr):

    # Moved xml_id from specific_data
    openupgrade.rename_xmlids(
        cr,
        [
            (f"specific_data.{xml_id}", f"alc_product_category_data.{xml_id}")
            for xml_id in IDS
        ],
    )
    # set xml_id on product.category records no_update=True
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data
        SET noupdate=True
        WHERE module='alc_product_category_data'
        AND name IN %s
    """,
        (tuple(IDS),),
    )

    # update existing food category
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref("alc_product_food.product_categ_ali").is_business_unit = True
