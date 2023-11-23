def migrate(cr, version=None):
    # rename group xml_id if not already done

    # check if old xml_id still exists
    cr.execute(
        "SELECT id FROM ir_model_data WHERE module = 'alc_eshop_form' AND name = 'eshop_form_manager_group' "
    )
    if cr.rowcount > 0:
        # rename xml_id
        # delete the new group referenced by the new xml_id
        cr.execute(
            "SELECT res_id FROM ir_model_data WHERE module = 'alc_eshop_api_forms' AND name = 'eshop_form_manager_group' "
        )
        new_group_id = cr.fetchone()[0]
        cr.execute("DELETE FROM ir_model_access WHERE group_id = %s", (new_group_id,))
        cr.execute("DELETE FROM res_groups WHERE id = %s", (new_group_id,))
        cr.execute(
            "DELETE FROM ir_model_data WHERE module = 'alc_eshop_api_forms' AND name = 'eshop_form_manager_group' "
        )
        # rename the xml_id
        cr.execute(
            "UPDATE ir_model_data  SET module = 'alc_eshop_api_forms' WHERE module = 'alc_eshop_form' AND name = 'eshop_form_manager_group' "
        )
