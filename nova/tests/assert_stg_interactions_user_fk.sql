select
    interactions.user_id,
    count(*) as row_count
from {{ ref('stg_interactions') }} as interactions
left join {{ ref('stg_users') }} as users
    on interactions.user_id = users.user_id
where users.user_id is null
group by 1
