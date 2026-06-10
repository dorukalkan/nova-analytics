select *
from {{ source('raw', 'nova_interactions') }}
