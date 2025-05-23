with
    source_sales_order_header_sales_reason_renamed as (
        select
            cast(salesorderid as int) as pk_sales_order
            , cast(salesreasonid as int) as fk_sales_reason
            , cast(modifieddate as datetime) as modified_date
        from {{ source('raw_adventure_works', 'salesorderheadersalesreason') }}
    )

select *
from source_sales_order_header_sales_reason_renamed
