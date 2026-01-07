from datetime import datetime
from functools import wraps

def log_operacao(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{agora}] A executar: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
