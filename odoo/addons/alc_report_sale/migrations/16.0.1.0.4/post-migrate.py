# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from psycopg2.extras import Json


@openupgrade.migrate()
def migrate(env, version):
    # update email template translation
    json_nl = Json(
        '<div style="margin: 0px; padding: 0px;">\n    '
        '<p style="margin: 0px; padding: 0px; font-size: 13px;">'
        "\n        Beste klant,\n        <br>\n        "
        'Wij danken u voor uw bestelling <t t-out="object.name'
        '">SO123456</t>.\n        <br>\n        Gelieve in bijlage de '
        "\n        <t t-if=\"ctx.get('proforma')\">\n           "
        "proforma factuur \n        </t>\n        <t t-else"
        '="">\n            offerte \n        </t>in PDF-formaat te vinden.'
        "\n        <br><br>\n        Met vriendelijke groeten.\n"
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
