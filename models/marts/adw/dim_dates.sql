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
            when extract(month from order_date) = 1 then 'jan'
            when extract(month from order_date) = 2 then 'feb'
            when extract(month from order_date) = 3 then 'mar'
            when extract(month from order_date) = 4 then 'apr'
            when extract(month from order_date) = 5 then 'may'
            when extract(month from order_date) = 6 then 'jun'
            when extract(month from order_date) = 7 then 'jul'
            when extract(month from order_date) = 8 then 'aug'
            when extract(month from order_date) = 9 then 'sep'
            when extract(month from order_date) = 10 then 'oct'
            when extract(month from order_date) = 11 then 'nov'
            when extract(month from order_date) = 12 then 'dec'
        end as order_month
        , extract(day from order_date) as order_day
    from dates
)

select *
from transform
