with
    source_state_province_renamed as (
        select
            cast(stateprovinceid as int) as pk_state_province
            , cast(countryregioncode as string) as fk_country_region_code
            , cast(territoryid as int) as fk_territory_id
            , cast(stateprovincecode as string) as state_province_code
            , cast(isonlystateprovinceflag as string) as is_only_state_province_flag
            , cast(name as string) as state_name
            , cast(modifieddate as date) as modified_date
        from {{ source('raw_adventure_works', 'stateprovince') }}
    )

select *
from source_state_province_renamed
