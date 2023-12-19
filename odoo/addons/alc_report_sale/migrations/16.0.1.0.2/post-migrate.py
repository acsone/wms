# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from psycopg2.extras import Json


@openupgrade.migrate()
def migrate(env, version):
    # update email template translation
    json_val = Json(
        '<div style="margin: 0px; padding: 0px;">\n    '
        '<p style="margin: 0px; padding: 0px; font-size: 13px;">'
        "\n        <t t-set=\"doc_name\" t-value=\"''devis'' if "
        "object.state in (''draft'', ''sent'') else ''commande''\">"
        "</t>\n        Cher Client,\n        <br>\n        "
        'Nous vous remercions pour votre commande <t t-out="object.name'
        '">SO123456</t>\n        <br>\n        Veuillez trouver ci-joint'
        "\n        <t t-if=\"ctx.get(''proforma'')\">\n            la "
        "facture proforma au format PDF.\n        </t>\n        <t t-else"
        '="">\n            le devis au format PDF.\n        </t>'
        "\n        <br><br>\n        Avec nos meilleures salutations.\n"
        "        <br>\n        Alcyon Belux SA\n    </p>\n</div>"
        "\n            "
    )
    query = f"""
            update mail_template
            set body_html = jsonb_set(body_html, '{{fr_BE}}', {json_val})
            where id = (select res_id from ir_model_data imd
                        where module = 'sale'
                        and name = 'email_template_edi_sale')
            """
    env.cr.execute(query)
