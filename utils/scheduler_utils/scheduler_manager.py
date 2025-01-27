from apscheduler.schedulers.asyncio import AsyncIOScheduler

"""
реализация singleton для scheduler
при необходимости допустимо реализовать получение через функцию  
def get_scheduler():
    # здесь что-то важное и причина зачем нужна эта функция 
    return scheduler
с импортом её ёв модулях потребителей и запускам
"""
scheduler = AsyncIOScheduler()
