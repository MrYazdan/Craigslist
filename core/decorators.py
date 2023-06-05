from time import sleep


def safe(except_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except:
                return except_value
        return wrapper
    return decorator