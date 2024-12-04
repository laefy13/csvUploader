from pathlib import Path
import os

UPLOAD_DIRECTORY = Path("..") / "storage" / "app" / "medalists"

UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

PIPELINE = [
    {
        '$group': {
            '_id': {
                'event': '$event',
                'discipline': '$discipline',
                'event_date': '$event_date'
            },
            'medalists': {
                '$push': '$$ROOT'
            }
        }
    },
    {
        '$project': {
            '_id': 0,
            'event': '$_id.event',
            'discipline': '$_id.discipline',
            'event_date': '$_id.event_date',
            'medalists': {
                '$map': {
                    'input': '$medalists',
                    'as': 'medalist',
                    'in': {
                        '$arrayToObject': {
                            '$filter': {
                                'input': {
                                    '$objectToArray': '$$medalist'
                                },
                                'as': 'field',
                                'cond': {
                                    '$and': [
                                        {'$ne': ['$$field.k', '_id']},
                                        {'$ne': ['$$field.k', 'event']},
                                        {'$ne': ['$$field.k', 'event_date']},
                                        {'$ne': ['$$field.k', 'discipline']}
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
    }
]
