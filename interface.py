from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from core import VkTools, Viewed
from database import Database
from config import comunity_token, acces_token, db_url_object

class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.db = Database(db_url_object)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()}
                              )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')
                elif command == 'поиск':
                    users = self.api.serch_users(self.params)
                    user = users.pop()

                    if self.db.check_profile_viewed(user['id']):
                        continue

                    missing_info = []
                    if not self.params['bdate']:
                        missing_info.append('дата рождения')
                    if not self.params['city']:
                        missing_info.append('город')
                    if not self.params['sex']:
                        missing_info.append('пол')
                    if not self.params['relation']:
                        missing_info.append('семейное положение')

                    if missing_info:
                        self.message_send(event.user_id, f'Для поиска пары необходимо указать следующую информацию: {", ".join(missing_info)}')
                        return

                    photos_user = self.api.get_photos(user['id'])

                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                        if num == 2:
                            break
                    self.message_send(event.user_id, f'Встречайте {user["name"]}', attachment=attachment)

                    self.db.add_viewed_profile(user['id'], 1)
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')

if __name__ == '__main__':
    community_token = "vk1.a.gDG2onsHHq-pvzLjMTXq4n140XK5PJuDFcV7N7kTBD1ULEf73sNuV9ARBmD23Sf5JXD36UEbw4s484C9_ShMqNJNhGwJ3QGn9UHafypxCTRu2ZLaTuDsQJg8CWfxy5wuA09SU4Xlzcc5tztxLpmJWYfAZ9XUyYqTNDttxrB9UDQNcdGove-vSAZ6zsKU7rI-99JOgIEeTi_yUWb8osFmDA"
    access_token = "vk1.a.3xBqNBSdAZaW0-x-m1elXhNSs5E414qbV7rZs3YyaLCIub23CXUUPGiRSQlhA8o5h7UcUK2ZEf_oSHYNoAX7rU8ATAbOO2XuZK88CovaDCl_z3jaWLTxHzJJxLlD4R3k0nGuPegB9OozS35FNOzfOwxwIcjiW1TWj31ACN_mPZLiTBSnGbISE-vY8-9gOws-2bmrcPsLQNr2_ujBlk66IQ"
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
