with
    source_sales_reason_renamed as (
        select
            cast(salesreasonid as int) as pk_sales_reason
            , case name
                when 'Price' then 'Preço'
                when 'On Promotion' then 'Promoção'
                when 'Manufacturer' then 'Fabricante'
                when 'Review' then 'Avaliação'
                when 'Quality' then 'Qualidade'
                when 'Television Advertisement' then 'Anúncio de Televisão'
                when 'Other' then 'Outro'
                else 'Desconhecido'
            end as sales_reason_name
            , cast(reasontype as string) as reason_type
            , cast(modifieddate as datetime) as modified_date
        from {{ source('raw_adventure_works', 'salesreason') }}
    )

select *
from source_sales_reason_renamed
