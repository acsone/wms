def migrate(cr, version=None):
    cr.execute(
        "update ir_model_data set res_id = (select id from keycloak_backend where name='Default') where module = 'connector_keycloak' and name='keycloak_backend'"
    )
    cr.execute("delete from keycloak_backend where name = 'keycloak';")
