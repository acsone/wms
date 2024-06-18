# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from psycopg2.extras import Json


@openupgrade.migrate()
def migrate(env, version):
    # update the email template
    openupgrade.load_data(env.cr, "alc_report_sale", "data/mail_template.xml")
    # update email template translation
    json_fr = Json(
        '<div style="margin: 0px; padding: 0px;">\n    '
        '<p style="margin: 0px; padding: 0px; font-size: 13px;">'
        "\n        Cher Client,\n        <br>\n        "
        "Nous vous remercions pour votre <t t-if=\"object.state in ('draft', 'sent')\">votre demande de prix</t>"
        '<t t-else="">commande</t> <t t-out="object.name'
        '">SO123456</t>.\n        <br>\n        Veuillez trouver ci-joint'
        "\n        <t t-if=\"ctx.get('proforma')\">\n            la "
        "facture proforma au format PDF.\n        </t>\n        <t t-else"
        '="">\n            <t t-if="object.state in (\'draft\', \'sent\')">le devis</t><t t-else="">la commande</t> au format PDF.\n        </t>'
        "\n        <br><br>\n        Avec nos meilleures salutations.\n"
        "        <br>\n        Alcyon Belux SA\n    </p>\n</div>"
        "\n            "
    )
    query = f"""
            update mail_template
            set body_html = jsonb_set(body_html, '{{fr_BE}}', {json_fr})
            where id = (select res_id from ir_model_data imd
                        where module = 'sale'
                        and name = 'email_template_edi_sale')
            """
    env.cr.execute(query)
    json_nl = Json(
        '<div style="margin: 0px; padding: 0px;">\n    '
        '<p style="margin: 0px; padding: 0px; font-size: 13px;">'
        "\n        Beste klant,\n        <br>\n        "
        'Wij danken u voor uw bestelling <t t-out="object.name'
        '">SO123456</t>.\n        <br>\n        In bijlage vindt u de '
        "\n        <t t-if=\"ctx.get('proforma')\">\n           "
        "proforma factuur in PDF-formaat.\n        </t>\n        <t t-else"
        '="">\n            offerte in PDF-formaat.\n        </t>'
        "\n        <br><br>\n        Hoogachtend.\n"
        "        <br>\n        Alcyon Belux SA\n    </p>\n</div>"
        "\n            "
    )
    query = f"""
            update mail_template
            set body_html = jsonb_set(body_html, '{{nl_BE}}', {json_nl})
            where id = (select res_id from ir_model_data imd
                        where module = 'sale'
                        and name = 'email_template_edi_sale')
            """
    env.cr.execute(query)
