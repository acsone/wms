import logging

_logger = logging.getLogger(__name__)

env = env  # noqa

es_backend = env.ref("alc_search_engine_backend.elasticsearch_backend")

_logger.info("Update sort script and ingest script on OpenSearch backend")
es_backend.reate_or_update_net_price_sort_script()
es_backend.create_or_update_current_price_pipeline_script()

_logger.info("Sync all keycloak users")
env["keycloak.user"].search([]).action_sync_keycloak_info()
env.cr.commit()

_logger.info("Sync Opensearch roles")
es_backend.synchronize_roles()
env.cr.commit()

_logger.info("Recompute all the products prices cache")
products = env["product.product"].search([])
size = 100
current = 0
total = len(products)
for batch in products.batch(100):
    _logger.info(
        "Recomputing prices cache for %s products (%s to %s on %s)",
        size,
        current,
        current + size,
        total,
    )
    batch.recompute_prices_cache()
    current += size
env.cr.commit()
