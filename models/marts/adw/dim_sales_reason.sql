with
    stg_sales_order_header_sales_reason as (
        select *
        from {{ ref('stg_adw__sales_order_header_sales_reason') }}
    )

    , stg_sales_reason as (
        select *
        from {{ ref('stg_adw__sales_reason') }}
    )

    , joined_sales_order_header_sales_reason as (
        select
            stg_sales_order_header_sales_reason.pk_sales_order
            , coalesce(stg_sales_reason.sales_reason_name, 'Unknown') as sales_reason_name
            , stg_sales_reason.reason_type
        from stg_sales_order_header_sales_reason
        left join stg_sales_reason
            on stg_sales_order_header_sales_reason.fk_sales_reason = stg_sales_reason.pk_sales_reason
    )

select *
from joined_sales_order_header_sales_reason