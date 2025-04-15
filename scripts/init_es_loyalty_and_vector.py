import logging

from tqdm import tqdm

_logger = logging.getLogger(__name__)

env = env  # noqa


es_backend = env.ref("alc_search_engine_backend.elasticsearch_backend")

batch_size = 10

if True:
    _logger.info("Compute vector index")
    products = env["product.product"].search([])
    for batch in tqdm(
        products.batch(batch_size),
        desc="Initalizing product's vector columns",
        unit=" batch",
        total=len(products) // batch_size,
    ):
        batch._compute_description_vector()
        batch._compute_characteristics_vector()
        env.cr.commit()

loyalty_programs = env["loyalty.program"].search([])

if True:
    _logger.info("Init loyalty_program_partner_rel")
    for program in tqdm(
        loyalty_programs, desc="Init loyalty_program_partner_rel", unit=" program"
    ):
        program._compute_all_restricted_partner_ids()
        env.cr.commit()

if True:
    _logger.info("Mark loyalty programs to export")
    loyalty_programs.filtered(lambda p: not p.is_published).action_toggle_is_published()
    env.cr.commit()

if True:
    _logger.info("Create loyalty program roles")
    loyalty_programs.delay_create_or_update_linked_role()
    env.cr.commit()
