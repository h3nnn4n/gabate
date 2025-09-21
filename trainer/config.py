from decouple import config
from dotenv import load_dotenv

load_dotenv()


## Algorithm settings

N_GENERATIONS = int(config("N_GENERATIONS", default=100, cast=int))
POPULATION_SIZE = int(config("POPULATION_SIZE", default=10, cast=int))

N_AGENT_EVALS = int(config("N_AGENT_EVALS", default=5, cast=int))

CROSSOVER_RATE = float(config("CROSSOVER_RATE", default=0.3, cast=float))
MUTATION_RATE = float(config("MUTATION_RATE", default=0.1, cast=float))

ELITE_MUTATIONS = int(config("ELITE_MUTATIONS", default=5, cast=int))

# Can be "max", "min", "avg", "sum" or "median"
FITNESS_MODE = str(config("FITNESS_MODE", default="max", cast=str))

N_GENES = int(config("N_GENES", default=14 * 3, cast=int))
FEATURE_SET_NAME = str(config("FEATURE_SET_NAME", default="LELmark", cast=str))
GENE_RANGE = float(config("GENE_RANGE", default=5.0, cast=float))
GENE_STEP_SIZE = float(config("GENE_STEP_SIZE", default=1.0, cast=float))

## Infrastructure settings

REDIS_URL: str = str(config("REDIS_URL", default="redis://localhost:6379"))

## Worker settings

WORKER_CONCURRENCY = int(config("WORKER_CONCURRENCY", default=1, cast=int))

## Misc

CAPTURE_OUTPUT = bool(config("CAPTURE_OUTPUT", default=False, cast=bool))