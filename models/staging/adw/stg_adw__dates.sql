with source as (
    select *
    from {{ source('raw_adventure_works', 'salesorderheader') }}
)
, dates as (
    select
        cast(orderdate as datetime) as order_date
    from source
)

select *
from dates
