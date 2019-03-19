# -*- coding: utf-8 -*-
# Copyright 2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def fix_lots(ctx):
    # Some lots do not have the expected product as entered at reception
    # The created quant has the correct product
    # Update those lots to set the product as defined on the quant
    spl = ctx.env['stock.production.lot']

    spl._get_fk_on('product_product')
    product_fields = dict(ctx.env.cr.fetchall())

    spl._get_fk_on('product_template')
    template_fields = dict(ctx.env.cr.fetchall())

    spl._get_fk_on(spl._table)
    lot_fields = ctx.env.cr.fetchall()

    lot_to_unlink = spl.browse()

    ctx.env.cr.execute(
        """
        select distinct q.lot_id
         , spl.name
         , spl.product_id AS bad_product_id
         , q.product_id AS good_product_id
        from stock_quant q
        join stock_production_lot spl on spl.id=q.lot_id
        where q.product_id!=spl.product_id
    """
    )
    for line in ctx.env.cr.dictfetchall():
        ctx.log_line(
            "Lot %s has product_id %s instead of %s"
            % (line['lot_id'], line['bad_product_id'], line['good_product_id'])
        )
        bad_lot = spl.browse(line['lot_id'])
        bad_lot_product_ids = bad_lot.mapped('quant_ids.product_id').ids
        if line['bad_product_id'] in bad_lot_product_ids:
            ctx.log_line("- lot is also correctly used. Keep it")
            keep_bad_lot = True
        else:
            keep_bad_lot = False

        # Does the right lot already exist?
        good_lot = spl.search(
            [
                ('name', '=', line['name']),
                ('product_id', '=', line['good_product_id']),
            ]
        )
        if not good_lot and keep_bad_lot:
            # Then we need to deduplicate the lot
            ctx.log_line("- deduplicate lot")
            good_lot = bad_lot.copy({'product_id': line['good_product_id']})
        elif not good_lot and not keep_bad_lot:
            # We can simply fix the product_id on the lot
            ctx.log_line("- fixing lot directly")
            ctx.env.cr.execute(
                """
                UPDATE stock_production_lot
                SET product_id = %s
                WHERE id = %s
            """,
                (line['good_product_id'], line['lot_id']),
            )

        else:
            ctx.log_line("- replacing links with lot %s" % good_lot.id)
            # We need to update all tables to link to the good lot
            for table, column in lot_fields:
                where = " WHERE " + column + "=%s "

                query = "SELECT count(*) FROM " + table + where
                ctx.env.cr.execute(query, (bad_lot.id,))
                count = ctx.env.cr.fetchone()[0]
                if not count:
                    continue

                join = ""
                if table in product_fields:
                    where += "AND {}={}".format(
                        product_fields[table], line['good_product_id']
                    )
                elif table in template_fields:
                    product = ctx.env['product.product'].browse(
                        line['good_product_id']
                    )
                    where += "AND {}={}".format(
                        template_fields[table], product.product_tmpl_id.id
                    )
                elif table == 'stock_pack_operation_lot':
                    join += """
                        JOIN stock_pack_operation spo
                        ON spo.id = stock_pack_operation_lot.operation_id
                        """
                    where += "AND spo.product_id=%s" % line['good_product_id']
                else:
                    ctx.log_line(
                        "- skipping {} rows in table {}".format(count, table)
                    )
                    continue

                query = "SELECT " + table + ".id FROM " + table + join + where
                ctx.env.cr.execute(query, (bad_lot.id,))
                ids = tuple([x[0] for x in ctx.env.cr.fetchall()])
                if not ids:
                    continue
                ctx.log_line("- fixing ids {} in table {}".format(ids, table))

                query = (
                    "UPDATE "
                    + table
                    + " SET "
                    + column
                    + "=%s"
                    + " WHERE id in %s"
                )
                ctx.log_line("  " + query % (good_lot.id, ids))
                ctx.env.cr.execute(query, (good_lot.id, ids))

            if not keep_bad_lot:
                lot_to_unlink |= bad_lot

    ctx.log_line("Deleting lots %s" % lot_to_unlink.ids)
    lot_to_unlink.unlink()
