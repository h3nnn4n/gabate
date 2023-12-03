import dramatiq
from decouple import config
from dotenv import load_dotenv
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from periodiq import PeriodiqMiddleware

load_dotenv()


REDIS_URL = config("REDIS_URL", default="redis://localhost:6379")


result_backend = RedisBackend(url=REDIS_URL)
broker = RedisBroker(url=REDIS_URL)
broker.add_middleware(Results(backend=result_backend))
broker.add_middleware(PeriodiqMiddleware(skip_delay=30))
dramatiq.set_broker(broker)

print("set configs")
