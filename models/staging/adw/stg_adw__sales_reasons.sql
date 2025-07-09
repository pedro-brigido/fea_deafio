with
    source_sales_reason_renamed as (
        select
            cast(salesreasonid as int) as pk_sales_reason
            , cast(coalesce(name, 'Unknown') as string) as sales_reason_name
            , cast(reasontype as string) as reason_type
            , cast(modifieddate as datetime) as modified_date
        from {{ source('raw_adventure_works', 'salesreason') }}
    )

select *
from source_sales_reason_renamed
