from enum import Enum

class Environment(Enum):
    PROD = "prod"
    RC = "rc"


TEST_MODELS = [
    {"model_name": "phi4-mini", 'app_id': "6a2e4a09efa04c1a6267a096", "service_name": "ollama-service-phi4"},  # new ollama phi4 app     
    {"model_name": "gpt-oss:20b", 'app_id': "6a2e407d2954388f96d61c6d",  "service_name": "ollama-service-gpt-oss"},  # new ollama gpt-oss-20b app
 ]

RUN_ENV = Environment.PROD
