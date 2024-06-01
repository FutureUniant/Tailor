from app.src.dao.browse_dao import BrowseDAO


class BrowseController:
    def __init__(self):
        self.browse_dao = BrowseDAO()

    def insert(self, browses):
        for browse in browses:
            select_browses = self.browse_dao.select_by_path(browse.path)
            if len(select_browses) == 0:
                self.browse_dao.insert([browse])

    def select_all(self, limit=5):
        return self.browse_dao.select_all(limit=limit)
