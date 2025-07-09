with
    source_sales_person_renamed as (
        select
            cast(businessentityid as int) as pk_business_entity
            , cast(territoryid as int) as fk_territory
            , cast(salesquota as int) as sales_quota
            , cast(bonus as int) as bonus
            , cast(commissionpct as float) as commission_pct
            , cast(salesytd as float) as sales_ytd
            , cast(saleslastyear as float) as sales_last_year
            , cast(modifieddate as datetime) as modified_date
        from {{ source('raw_adventure_works', 'salesperson') }}
    )

select *
from source_sales_person_renamed
