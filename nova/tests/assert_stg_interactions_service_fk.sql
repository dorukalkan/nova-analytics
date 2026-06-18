select
    interactions.service_id,
    count(*) as row_count
from {{ ref('stg_interactions') }} as interactions
left join {{ ref('stg_services') }} as services
    on interactions.service_id = services.service_id
where services.service_id is null
group by 1
