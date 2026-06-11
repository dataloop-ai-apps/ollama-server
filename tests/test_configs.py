from enum import Enum

class Environment(Enum):
    PROD = "prod"
    RC = "rc"

TEST_MODELS = {
    'phi4_mini': {'app_id': "69f347caa2fa3b9be0499b31", "model_name": "phi4-mini"},
    'gpt_oss_20b': {'app_id': "69f347caa2fa3b9be0499b31", "model_name": "phi4-mini"}
    # 'gpt-oss-20b': {'app_id': "69f347caa2fa3b9be0499b31", "model_name": "gpt-oss-20b"}
}

RUN_ENV = Environment.PROD

