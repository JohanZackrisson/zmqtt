from pymongo import MongoClient
import datetime
import time


class MongoLog(object):

    def __init__(self, db, collection):
        self._client = MongoClient()
        self._db = self._client[db]
        self._collection = self._db[collection]
        self._lastUpdate = 0

    def Log(self, data):
        cdata = data.copy()
        self._lastUpdate = time.time()
        return self._collection.insert_one(cdata).inserted_id

    def Collection(self):
        return self._collection

    def Query(self):
        return self._collection.find()

    def LastUpdate(self):
        return self._lastUpdate


def test():
    log = MongoLog("test_db", "test_logs")

    post = {"author": "Mike",
            "text": "My first blog post!",
            "tags": ["mongodb", "python", "pymongo"],
            "date": datetime.datetime.utcnow()}
    log.Log(post)

    for item in log.Query():
        print(item)

if __name__ == '__main__':
    test()
