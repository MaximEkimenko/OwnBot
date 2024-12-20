
def joined_to_dict(user_model, user_dict: dict, joined_models: list) -> dict:
    """Добавление словарей связанных моделей"""
    for model in joined_models:
        user_dict[user_model.telegram_id].update({repr(model): [data.to_dict() for data in joined_models]})
    return user_dict
