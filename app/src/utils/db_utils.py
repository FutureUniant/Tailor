


def db_connect_deal(db_helper):
    def outwrapper(func):
        def wrapper(*args, **kwargs):
            db_helper.connect()
            out = func(*args, **kwargs)
            db_helper.close()
            return out
        return wrapper
    return outwrapper