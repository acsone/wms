-- Deal with duplicated CNK codes (should be unique) by adding a '#<id>' suffix

-- Manual query to check for duplicates::
-- select cnk_code from product_template where cnk_code is not null and trim(cnk_code) != '' group by cnk_code having count(*) > 1;

-- Get rid of the archived products first, to eventually reduce the number of active entries updated
update product_template
set cnk_code = cnk_code || '#' || id
where cnk_code in (
    select cnk_code
    from product_template
    where cnk_code is not null and trim(cnk_code) != ''
    group by cnk_code having count(*) > 1
) and active = false;

-- Then check if there are still duplicates with the active entries
update product_template
set cnk_code = cnk_code || '#' || id
where cnk_code in (
    select cnk_code
    from product_template
    where cnk_code is not null and trim(cnk_code) != ''
    group by cnk_code having count(*) > 1
);
