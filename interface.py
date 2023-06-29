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

    def handle_parameters(self, user_id, command):
        if command == 'параметры':
            self.message_send(user_id, 'Введите параметры в формате: возраст, пол, город, семейное положение')
        else:
            parameters = command.split(',')
            if len(parameters) != 4:
                self.message_send(user_id, 'Некорректный формат параметров. Введите параметры в формате: возраст, пол, город, семейное положение')
                return
            
            age, sex, city, relation = [param.strip() for param in parameters]

            self.params['bdate'] = datetime.now().strftime('%d.%m.%Y')
            self.params['sex'] = 1 if sex.lower() == 'женский' else 2
            self.params['city'] = city.strip()
            self.params['relation'] = relation.strip()

            self.message_send(user_id, 'Параметры успешно обновлены. Вы можете использовать команду "поиск" для поиска пары.')

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуй, {self.params["name"]}!')
                elif command == 'параметры' or command.startswith('параметры:'):
                    self.handle_parameters(event.user_id, command)
                elif command == 'поиск':
                    if any(param is None for param in self.params.values()):
                        self.message_send(event.user_id, 'Для поиска пары необходимо указать параметры. Введите "параметры" для задания параметров.')
                        continue

                    users = self.api.serch_users(self.params)
                    user = users.pop()

                    if self.db.check_profile_viewed(user['id']):
                        continue

                    photos_user = self.api.get_photos(user['id'])

                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                        if num == 2:
                            break
                    self.message_send(event.user_id, f'Встречайте {user["name"]}!', attachment=attachment)

                    self.db.add_viewed_profile(user['id'], 1)
                elif command == 'пока':
                    self.message_send(event.user_id, 'Пока!')
                else:
                    self.message_send(event.user_id, 'Команда не опознана.')

if __name__ == '__main__':
    community_token = "vk1.a.gDG2onsHHq-pvzLjMTXq4n140XK5PJuDFcV7N7kTBD1ULEf73sNuV9ARBmD23Sf5JXD36UEbw4s484C9_ShMqNJNhGwJ3QGn9UHafypxCTRu2ZLaTuDsQJg8CWfxy5wuA09SU4Xlzcc5tztxLpmJWYfAZ9XUyYqTNDttxrB9UDQNcdGove-vSAZ6zsKU7rI-99JOgIEeTi_yUWb8osFmDA"
    access_token = "vk1.a.3xBqNBSdAZaW0-x-m1elXhNSs5E414qbV7rZs3YyaLCIub23CXUUPGiRSQlhA8o5h7UcUK2ZEf_oSHYNoAX7rU8ATAbOO2XuZK88CovaDCl_z3jaWLTxHzJJxLlD4R3k0nGuPegB9OozS35FNOzfOwxwIcjiW1TWj31ACN_mPZLiTBSnGbISE-vY8-9gOws-2bmrcPsLQNr2_ujBlk66IQ"
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
