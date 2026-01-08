from datetime import datetime
from functools import wraps


def log_operacao(func):
    """
    Regista data/hora e nome da função.
    Também apanha exceções e volta a lançar (para não esconder erros).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{agora}] A executar: {func.__name__}")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[ERRO] {func.__name__}: {e}")
            raise
    return wrapper
