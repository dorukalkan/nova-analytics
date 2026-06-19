select
    interactions.service_id,
    interactions.category as interaction_category,
    services.category as service_category,
    count(*) as row_count
from {{ ref('stg_interactions') }} as interactions
left join {{ ref('stg_services') }} as services
    on interactions.service_id = services.service_id
where interactions.category != services.category
    or services.service_id is null
group by 1, 2, 3
