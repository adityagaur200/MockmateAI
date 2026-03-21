from bson import ObjectId


def serialize_mongo(document):
    document["_id"] = str(document["_id"])
    return document