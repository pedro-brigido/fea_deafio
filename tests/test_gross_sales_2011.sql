/* Verify that gross sales from 2011 match the expected value.*/

with 
    gross_total_2011 as (
        select
            cast(sum(gross_total) as numeric(18, 4)) as gross_total_2011
        from {{ ref('fct_sales_orders') }}
        where extract(year from order_date) = 2011
    )

select *
from gross_total_2011
where abs(gross_total_2011.gross_total_2011 - 12646112.16) > 0.01
