from redis import Redis
from rq import Queue

from app.config import settings

redis_conn = Redis.from_url(settings.redis_url)
render_queue = Queue("shortsforge", connection=redis_conn, default_timeout=1800)
