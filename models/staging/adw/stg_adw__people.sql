with source_person_renamed as (
    select
        cast(businessentityid as int) as pk_business_entity
        , case persontype
            when 'EM' then 'Employee'
            when 'IN' then 'Individual Customer'
            when 'SC' then 'Store Contact'
            when 'SP' then 'Sales Person'
            when 'VC' then 'Vendor Contact'
            when 'GC' then 'General Contact'
            else 'Unknown'
        end as person_type
        , cast(firstname as string) as first_name
        , cast(middlename as string) as middle_name
        , cast(lastname as string) as last_name
        , cast(
            (coalesce(firstname, '') || ' ' || coalesce(middlename, '') || ' ' || coalesce(lastname, ''))
            as string
        ) as full_name
    from {{ source('raw_adventure_works', 'person') }}
)

select *
from source_person_renamed
