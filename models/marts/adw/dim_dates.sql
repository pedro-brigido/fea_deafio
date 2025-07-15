with 
    dates as (
        select *
        from {{ ref('stg_adw__dates') }}
)
, transform as (
    select
        order_date
        , extract(year from order_date) as order_year
        , case
            when extract(month from order_date) = 1 then 'Jan'
            when extract(month from order_date) = 2 then 'Feb'
            when extract(month from order_date) = 3 then 'Mar'
            when extract(month from order_date) = 4 then 'Apr'
            when extract(month from order_date) = 5 then 'May'
            when extract(month from order_date) = 6 then 'Jun'
            when extract(month from order_date) = 7 then 'Jul'
            when extract(month from order_date) = 8 then 'Aug'
            when extract(month from order_date) = 9 then 'Sep'
            when extract(month from order_date) = 10 then 'Oct'
            when extract(month from order_date) = 11 then 'Nov'
            when extract(month from order_date) = 12 then 'Dec'
        end as order_month
        , extract(day from order_date) as order_day
    from dates
)

select 
    *
    , cast(concat(order_month, order_year) as string) as year_month
from transform
