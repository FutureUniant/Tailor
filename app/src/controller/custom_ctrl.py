from app.src.dao.custom_dao import CustomDAO


class CustomController:
    def __init__(self):
        self.custom_dao = CustomDAO()

    def insert(self, customs):
        self.custom_dao.insert(customs)

    def delete(self, customs):
        self.custom_dao.delete(customs)

    def update(self, customs):
        self.custom_dao.update(customs)

    def select_all(self):
        return self.custom_dao.select_all()
