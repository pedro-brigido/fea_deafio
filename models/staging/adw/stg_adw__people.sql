with source_person_renamed as (
    select
        cast(businessentityid as int) as pk_business_entity
        , case persontype
            when 'EM' then 'Empregado'
            when 'IN' then 'Cliente Individual'
            when 'SC' then 'Contato da loja'
            when 'SP' then 'Vendedor'
            when 'VC' then 'Contato de fornecedor'
            when 'GC' then 'Contato geral'
            else 'Desconhecido'
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
