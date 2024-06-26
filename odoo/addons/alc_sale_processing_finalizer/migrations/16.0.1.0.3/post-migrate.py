# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from psycopg2.extras import Json


@openupgrade.migrate()
def migrate(env, version):
    # update the email template
    openupgrade.load_data(
        env.cr, "alc_sale_processing_finalizer", "data/mail_template_30.xml"
    )
    # update email template translation
    json_fr = Json(
        """
<t t-set="lines" t-value="object._get_sales_bo_gt_3months_lines(object)" />
<p>Bonjour,<br/></p>
<p>Les articles non disponibles de votre commande <t t-out="object.name">SO123456</t> ont été annulés car la commande a plus de 3 mois.<br/></p>
<p t-if="lines">
Le(s) article(s) concerné(s) sont :
<ul>
    <li t-foreach="lines" t-as="line"><t t-esc="line.product_id.display_name" /></li>
</ul>
</p>
<p>Vous n’avez rien à faire, l’annulation est automatique.</p>

Si vous le souhaitez, vous pouvez recommander ces articles via le site, ou en prenant contact avec le Service Client : customerservice@alcyonbelux.be
        """
    )
    query = f"""
            update mail_template
            set body_html = jsonb_set(body_html, '{{fr_BE}}', {json_fr})
            where id = (select res_id from ir_model_data imd
                        where module = 'alc_sale_processing_finalizer'
                        and name = 'mail_template_30')
            """
    env.cr.execute(query)
    json_nl = Json(
        """
<t t-set="lines" t-value="object._get_sales_bo_gt_3months_lines(object)" />
<p>Beste,<br/></p>
<p>De niet beschikbare artikelen in uw bestelling <t t-out="object.name">SO123456</t> zijn geannuleerd omdat de bestelling meer dan 3 maanden oud is.<br/></p>
<p t-if="lines">
De betreffende artikelen zijn :
<ul>
    <li t-foreach="lines" t-as="line"><t t-esc="line.product_id.display_name" /></li>
</ul>
</p>
<p>U hoeft niets te doen, de annulering gebeurt automatisch.</p>

Als u wenst kan u deze artikelen opnieuw bestellen via de site, of door contact op te nemen met de klantenservice: customerservice@alcyonbelux.be
        """
    )
    query = f"""
            update mail_template
            set body_html = jsonb_set(body_html, '{{nl_BE}}', {json_nl})
            where id = (select res_id from ir_model_data imd
                        where module = 'alc_sale_processing_finalizer'
                        and name = 'mail_template_30')
            """
    env.cr.execute(query)

    json_en = Json(
        """
<t t-set="lines" t-value="object._get_sales_bo_gt_3months_lines(object)" />
<p>Hello,<br/></p>
<p>Unavailable items from your order <t t-out="object.name">SO123456</t> have been canceled because the order is more than 3 months old.<br/></p>
<p t-if="lines">
The item(s) concerned are:
<ul>
    <li t-foreach="lines" t-as="line"><t t-esc="line.product_id.display_name" /></li>
</ul>
</p>
<p>You don't have to do anything, cancellation is automatic.</p>

If you wish, you can order again these items on our website, or via our Customer Service: customerservice@alcyonbelux.be
        """
    )
    query = f"""
                update mail_template
                set body_html = jsonb_set(body_html, '{{en_US}}', {json_en})
                where id = (select res_id from ir_model_data imd
                            where module = 'alc_sale_processing_finalizer'
                            and name = 'mail_template_30')
                """
    env.cr.execute(query)
