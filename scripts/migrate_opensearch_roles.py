import logging

_logger = logging.getLogger(__name__)

env = env  # noqa

es_backend = env.ref("alc_search_engine_backend.elasticsearch_backend")

_logger.info("Update sort script and ingest script on OpenSearch backend")
es_backend.create_or_update_net_price_sort_script()
es_backend.create_or_update_current_price_pipeline_script()

_logger.info("Sync all keycloak users")
env["keycloak.user"].search([]).action_sync_keycloak_info()
env.cr.commit()

# ensure roles are cleaned up
_logger.info("Clean Opensearch roles")
env.cr.execute(
    """
    DELETE FROM elasticsearch_role
    WHERE vt_group_id is not null or pricelist_id is not null
"""
)
_logger.info("Create pricelist roles")
env["product.pricelist"].search([]).delay_create_or_update_linked_role()
env.cr.commit()

_logger.info("Create vt_group roles")
env["veterinary.group"].search([]).delay_create_or_update_linked_role()
env.cr.commit()


_logger.info("Recompute all the products prices cache")
products = env["product.product"].search([])
size = 10
current = 0
total = len(products)
for batch in products.batch(size):
    _logger.info(
        "Recomputing prices cache for %s products (%s to %s on %s)",
        size,
        current,
        current + size,
        total,
    )
    batch._delay_update_price_cache()
    current += size
    env.cr.commit()
