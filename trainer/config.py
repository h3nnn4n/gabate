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


N_GENERATIONS = config("N_GENERATIONS", default=100, cast=int)
POPULATION_SIZE = config("POPULATION_SIZE", default=10, cast=int)

N_AGENT_EVALS = config("N_AGENT_EVALS", default=5, cast=int)

CROSSOVER_RATE = config("CROSSOVER_RATE", default=0.3, cast=float)
MUTATION_RATE = config("MUTATION_RATE", default=0.1, cast=float)

ELITE_MUTATIONS = config("ELITE_MUTATIONS", default=5, cast=int)
