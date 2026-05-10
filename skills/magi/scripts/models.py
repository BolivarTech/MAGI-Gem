# Minimal models.py for 1:1 migration
MODE_DEFAULT_MODELS = {
    "code-review": "opus",
    "design": "opus",
    "analysis": "sonnet",
}

MODEL_IDS = {
    "opus": "claude-3-opus-20240229",
    "sonnet": "claude-3-5-sonnet-20240620",
    "haiku": "claude-3-haiku-20240307",
}

VALID_MODELS = list(MODEL_IDS.keys())


def resolve_model(model_name: str) -> str:
    return MODEL_IDS.get(model_name, MODEL_IDS["opus"])
