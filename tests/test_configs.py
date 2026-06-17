from enum import Enum

class Environment(Enum):
    PROD = "prod"
    RC = "rc"

PROJECT_ID = "afd5a953-b88d-439c-afdf-9486ab3a94c2"


TEST_MODELS = [
    {"model_name": "gpt-oss:20b","dpk_name": "ollama-server-gpt-oss-20b",  "service_name": "ollama-service-gpt-oss-20b"},    
    {"model_name": "qwen3.5:9b", "dpk_name": "ollama-server-qwen35", "service_name": "ollama-service-qwen35"}, 
    {"model_name": "phi4-mini","dpk_name": "ollama-server-phi4", "service_name": "ollama-service-phi4"}, 
]


RUN_ENV = Environment.PROD
