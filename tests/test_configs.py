from enum import Enum

class Environment(Enum):
    PROD = "prod"
    RC = "rc"


TEST_MODELS = [
    {"model_name": "qwen3.5:9b", 'app_id': "6a2f97fdb38ee87527a3b3ca",  "service_name": "ollama-service-qwen35"},  # new qwen 3.5   
    {"model_name": "phi4-mini", 'app_id': "6a2f7918e1941e405f3d4aa4", "service_name": "ollama-service-phi4"},  # new ollama phi4 app     
 ]

RUN_ENV = Environment.PROD
