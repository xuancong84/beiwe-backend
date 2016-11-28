import mongolia
from pymongo import HASHED, ASCENDING

base = mongolia.mongo_connection.CONNECTION.get_connection()['beiwe']
chunk_registry = base.get_collection("chunk_registry")

print "indexing study_id..."
chunk_registry.create_index([('study_id', HASHED)])

print "indexing data_type..."
chunk_registry.create_index([('data_type', HASHED)])

print "indexing user_id..."
chunk_registry.create_index([('user_id', HASHED)])

print "indexing survey_id..."
chunk_registry.create_index([('survey_id', HASHED)])

print "indexing time_bin..."
chunk_registry.create_index([('time_bin', ASCENDING)])

print "these indexes exist"
indexes = [index.to_dict()['key'].items()[0] for index in chunk_registry.list_indexes()]
for name, index_type in indexes:
    index_type = "ascending" if index_type is 1 else index_type
    index_type = "descending" if index_type is -1 else index_type
    print name, ":", index_type.upper()
