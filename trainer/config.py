from decouple import config
from dotenv import load_dotenv

from redis import Redis

load_dotenv()


REDIS_URL: str = str(config("REDIS_URL", default="redis://localhost:6379"))

N_GENERATIONS = config("N_GENERATIONS", default=100, cast=int)
POPULATION_SIZE = config("POPULATION_SIZE", default=10, cast=int)

N_AGENT_EVALS = config("N_AGENT_EVALS", default=5, cast=int)

CROSSOVER_RATE = config("CROSSOVER_RATE", default=0.3, cast=float)
MUTATION_RATE = config("MUTATION_RATE", default=0.1, cast=float)

ELITE_MUTATIONS = config("ELITE_MUTATIONS", default=5, cast=int)

# Can be "max", "min", "avg", "sum" or "median"
FITNESS_MODE = config("FITNESS_MODE", default="max", cast=str)

FEATURE_SET_NAME = config("FEATURE_SET_NAME", default="LELmark", cast=str)
