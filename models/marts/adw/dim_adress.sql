with
    stg_address as (
        select *
        from {{ ref('stg_adw__address') }}
    )

    , stg_state_province as (
        select *
        from {{ ref('stg_adw__state_province') }}
    )

    , stg_country_region as (
        select *
        from {{ ref('stg_adw__country_region') }}
    )

    , joined_tables as (
        select
            stg_address.pk_address
            , stg_address.fk_state_province
            , stg_state_province.fk_country_region_code
            , stg_country_region.country_name
            , stg_state_province.state_name
            , stg_address.city
        from stg_address
        left join stg_state_province
            on stg_address.fk_state_province = stg_state_province.pk_state_province
        left join stg_country_region
            on stg_state_province.fk_country_region_code = stg_country_region.pk_country_region_code
    )

select *
from joined_tables