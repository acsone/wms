"""Merge manually created intrastat codes into records from the official account_intrastat module."""

from collections import defaultdict

from openupgradelib.openupgrade_merge_records import merge_records

env = env  # noqa

query = """\
    select
      aic.id,
      code,
      imd.name as xml_id,
      imd.module as module
    from account_intrastat_code aic
    left join ir_model_data imd on imd.res_id=aic.id and imd.model='account.intrastat.code'
    where aic.type = 'commodity'
    """

official_codes = {}
custom_codes = defaultdict(list)

env.cr.execute(query)
for rec_id, code, _, module in env.cr.fetchall():
    if module == "account_intrastat":
        assert code not in official_codes, f"Duplicate official code {code}"
        official_codes[code] = rec_id
    else:
        custom_codes[code].append(rec_id)

custom_codes_to_merge = set(custom_codes.keys()) & set(official_codes.keys())
print(f"Found {len(custom_codes_to_merge)} custom codes to merge")

for code, custom_ids in custom_codes.items():
    if code not in official_codes:
        print(f"Custom code {code} (ids={custom_ids}) not found in official codes")
        continue
    official_id = official_codes[code]
    print(
        f"Updating custom code {code} (ids={custom_ids}) "
        f"to official code {code} (id={official_id})"
    )
    merge_records(
        env,
        "account.intrastat.code",
        custom_ids,
        official_id,
        field_spec={"openupgrade_other_fields": "preserve"},
        method="orm",
        delete=True,
        exclude_columns=None,
        model_table=None,
    )
    env.cr.commit()
