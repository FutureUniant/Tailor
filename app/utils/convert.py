

class Dict2Class:
    def __init__(self, dictionary: dict):
        for key, val in dictionary.items():
            setattr(self, key, val)
