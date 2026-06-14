from enum import Enum

class Environment(Enum):
    PROD = "prod"
    RC = "rc"


TEST_MODELS = [
    {"model_name": "phi4-mini", 'app_id': "6a2ea553e1941e405f3d2d4d", "service_name": "ollama-service-phi-4-6a2ea553e194z"},  # new ollama phi4 app     
    {"model_name": "gpt-oss:20b", 'app_id': "6a2eb4adb1b05b0a5bc9c885",  "service_name": "ollama-service-gpt-oss-20-b-6a2ebz"},  # new ollama gpt-oss-20b app
 ]

RUN_ENV = Environment.PROD
