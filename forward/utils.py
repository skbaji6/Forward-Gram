async def get_next_value(db, seq_name):
    return db.sequences.find_and_modify(
        query={'collection': seq_name},
        update={'$inc': {'id': 1}},
        fields={'id': 1, '_id': 0},
        new=True
    ).get('id')
