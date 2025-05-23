with
    source_country_region_renamed as (
        select
            cast (countryregioncode as string) as pk_country_region_code		
            , cast (name as string) as country_name
        from {{ source('raw_adventure_works', 'countryregion') }}
    )

select *
from source_country_region_renamed
