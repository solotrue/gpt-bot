import pymongo
from config import MONGO_USERNAME, MONGO_PASSWORD, MONGO_DATABASE, MONGO_URL, MONGO_PORT


class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_URL, MONGO_PORT, username=MONGO_USERNAME, password=MONGO_PASSWORD)
        self.db = self.client[MONGO_DATABASE]
        self.contexts = self.db.contexts

    def save_context(self, chat_id, message_text, response):
        context_items = [{'message': message_text, 'response': response}]
        document = self.contexts.find_one({'chat_id': chat_id})

        if document:
            # Append this message and response to the existing context
            context_items = document['context']
            if isinstance(context_items, str):
                # Convert string to list of dictionaries
                context_items = [{'message': context_items, 'response': ''}]
            context_items.append({'message': message_text, 'response': response})

        document = {'chat_id': chat_id, 'context': context_items}
        self.contexts.replace_one({'chat_id': chat_id}, document, upsert=True)

    def reset_context(self, chat_id):
        update_result = self.contexts.update_one({'chat_id': chat_id}, {'$set': {'chat_id': 'reset_' + str(chat_id)}})

        if update_result.modified_count == 0:
            raise ValueError("No conversation context found with given chat_id.")
