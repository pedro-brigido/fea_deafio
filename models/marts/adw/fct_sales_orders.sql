with
    stg_sales_order_header as (
        select *
        from {{ ref('stg_adw__sales_order_headers') }}
    )

    , stg_sales_order_detail as (
        select *
        from {{ ref('stg_adw__sales_order_details') }}
    )

    , enriched_sales_order as (
        select
            stg_sales_order_header.pk_sales_order
            , stg_sales_order_header.fk_customer
            , stg_sales_order_detail.fk_product
            , stg_sales_order_header.fk_ship_to_address
            , stg_sales_order_header.fk_credit_card
            , stg_sales_order_header.order_date
            , stg_sales_order_header.due_date
            , stg_sales_order_header.ship_date
            , stg_sales_order_header.status
            , stg_sales_order_detail.order_quantity
            , stg_sales_order_detail.unit_price
            , stg_sales_order_detail.unit_price_discount
        from stg_sales_order_header
        left join stg_sales_order_detail
            on stg_sales_order_header.pk_sales_order = stg_sales_order_detail.fk_sales_order
    )

    , metrics_calculation as (
        select 
            *
            , order_quantity * unit_price as gross_total
            , order_quantity * unit_price * (1 - unit_price_discount) as net_total
            , datediff('day', order_date, ship_date) as lead_time_shipping
            , case 
                when 
                    ship_date > due_date then TRUE 
                else FALSE 
            end as order_delayed
            , unit_price_discount > 0 as discount_applied
        from enriched_sales_order
    )

select * 
from metrics_calculation
