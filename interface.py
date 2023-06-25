import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from core import VkTools, Viewed

class BotInterface:
    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send', {
            'user_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': get_random_id()
        })

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')
                elif command == 'поиск':
                    users = self.api.search_users(self.params)
                    user = users.pop()
                    viewed = session.query(Viewed).filter(Viewed.profile_id == user['id']).first()
                    if viewed:
                        continue
                    photos_user = self.api.get_photos(user['id'])
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                        if num == 2:
                            break
                    self.message_send(event.user_id, f'Встречайте {user["name"]}', attachment=attachment)
                    viewed = Viewed(profile_id=user['id'], worksheet_id=1)
                    session.add(viewed)
                    session.commit()
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    community_token = "vk1.a.gDG2onsHHq-pvzLjMTXq4n140XK5PJuDFcV7N7kTBD1ULEf73sNuV9ARBmD23Sf5JXD36UEbw4s484C9_ShMqNJNhGwJ3QGn9UHafypxCTRu2ZLaTuDsQJg8CWfxy5wuA09SU4Xlzcc5tztxLpmJWYfAZ9XUyYqTNDttxrB9UDQNcdGove-vSAZ6zsKU7rI-99JOgIEeTi_yUWb8osFmDA"
    access_token = "vk1.a.3xBqNBSdAZaW0-x-m1elXhNSs5E414qbV7rZs3YyaLCIub23CXUUPGiRSQlhA8o5h7UcUK2ZEf_oSHYNoAX7rU8ATAbOO2XuZK88CovaDCl_z3jaWLTxHzJJxLlD4R3k0nGuPegB9OozS35FNOzfOwxwIcjiW1TWj31ACN_mPZLiTBSnGbISE-vY8-9gOws-2bmrcPsLQNr2_ujBlk66IQ&expires_in=86400&user_id=6197006"
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
