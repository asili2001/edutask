import pytest
import pymongo
import json
from src.util.dao import DAO
from src.util.validators import getValidator
import pymongo.errors
from bson import ObjectId
from unittest.mock import patch, MagicMock
from pymongo.errors import WriteError

@pytest.fixture
def mock_validator():
    with open('./src/static/validators/todo.json') as f:
        return json.load(f)

@pytest.fixture
def dao_simulated_mongo(mock_validator):
    with patch('src.util.dao.getValidator', return_value=mock_validator), \
         patch('pymongo.MongoClient') as mock_client:

        fake_store = {}
        fake_id = ObjectId("507f191e810c19729de860ea")

        def insert_one(doc):
            # Simulate MongoDB validator behavior
            if 'description' not in doc:
                raise WriteError("Missing required field: description")

            if not isinstance(doc.get("done"), bool):
                raise WriteError("Field 'done' must be a boolean")

            key = str(doc.get("description"))
            if key in fake_store:
                raise WriteError("Duplicate key")

            doc['_id'] = fake_id
            fake_store[key] = doc

            res = MagicMock()
            res.inserted_id = fake_id
            return res

        def find_one(query):
            for doc in fake_store.values():
                if doc['_id'] == query['_id']:
                    return doc
            return None

        def find(query=None):
            return list(fake_store.values())

        mock_collection = MagicMock()
        mock_collection.insert_one.side_effect = insert_one
        mock_collection.find_one.side_effect = find_one
        mock_collection.find.side_effect = find

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ['test_collection']
        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.edutask = mock_db

        dao = DAO("test_collection")
        return dao


def test_create_valid_document(dao_simulated_mongo):
    data = {
        "description": "Task A",
        "done": True
    }
    result = dao_simulated_mongo.create(data)
    assert result['description'] == "Task A"
    assert result['done'] is True

def test_create_missing_required_field(dao_simulated_mongo):
    data = {
        "done": False
    }

    with pytest.raises(WriteError, match="Missing required field"):
        dao_simulated_mongo.create(data)

def test_create_invalid_field_type(dao_simulated_mongo):
    data = {
        "description": "Invalid",
        "done": "yes"
    }

    with pytest.raises(WriteError, match="Field 'done' must be a boolean"):
        dao_simulated_mongo.create(data)

def test_create_duplicate_document(dao_simulated_mongo):
    data = {
        "description": "Unique Task",
        "done": True
    }

    dao_simulated_mongo.create(data)

    with pytest.raises(WriteError, match="Duplicate key"):
        dao_simulated_mongo.create(data)