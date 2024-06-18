def migrate(cr, version):
    """Mark module to install."""
    cr.execute(
        """
        UPDATE ir_module_module SET state = 'to install'
        WHERE name = 'alc_elasticsearch_security_legacy_support'
        """
    )
    # get the number of rows affected
    row_count = cr.rowcount
    if not row_count:
        raise Exception(
            "Module alc_elasticsearch_security_legacy_support not found. "
            "PLZ update module list before"
        )
