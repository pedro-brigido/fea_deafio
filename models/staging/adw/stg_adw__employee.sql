with
    source_employee_renamed as (
        select
            cast(businessentityid as int) as pk_business_entity
            , cast(nationalidnumber as int) as national_id_number
            , cast(loginid as string) as login_id
            , cast(jobtitle as string) as job_tittle
            , cast(birthdate as date) as birth_date
            , case
                when maritalstatus = 'S' then 'Single'
                when maritalstatus = 'M' then 'Married'
            end as marital_status
            , case
                when gender = 'M' then 'Male'
                when gender = 'F' then 'Female'
            end as gender
            , cast(hiredate as date) as hire_date
            , cast(salariedflag as boolean) as salaried_flag
            , cast(vacationhours as int) as vacation_hours
            , cast(sickleavehours as int) as sick_leave_hours
            , cast(currentflag as boolean) as current_flag
            , cast(modifieddate as datetime) as modified_date
            , cast(organizationnode as string) as organization_node
        from {{ source('raw_adventure_works', 'employee') }}
    )

select *
from source_employee_renamed
