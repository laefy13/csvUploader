from bson import ObjectId
from fastapi.encoders import jsonable_encoder

def custom_jsonable_encoder(obj, *args, **kwargs):
    if isinstance(obj, ObjectId):
        return str(obj)
    return jsonable_encoder(obj, *args, **kwargs)