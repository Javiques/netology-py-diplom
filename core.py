from datetime import datetime
import vk_api
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class VkTools:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)
        engine = create_engine(db_url_object)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get_profile_info(self, user_id):
        info = self.api.method('users.get', {'user_ids': user_id, 'fields': 'city,bdate,sex,relation,home_town'})
        info = info[0]
        user_info = {
            'name': info['first_name'] + ' ' + info['last_name'],
            'id': info['id'],
            'bdate': info.get('bdate'),
            'home_town': info.get('home_town'),
            'sex': info['sex'],
            'city': info['city']['id']
        }
        return user_info

    def search_users(self, params):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        current_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = current_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method('users.search', {
            'count': 10,
            'offset': 0,
            'age_from': age_from,
            'age_to': age_to,
            'sex': sex,
            'city': city,
            'status': 6,
            'is_closed': False
        })

        users = users['items'] if 'items' in users else []

        res = []
        for user in users:
            if not user['is_closed']:
                res.append({'id': user['id'], 'name': user['first_name'] + ' ' + user['last_name']})

        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get', {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        })

        photos = photos['items'] if 'items' in photos else []

        res = []
        for photo in photos:
            res.append({
                'owner_id': photo['owner_id'],
                'id': photo['id'],
                'likes': photo['likes']['count'],
                'comments': photo['comments']['count']
            })

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)

        return res


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = Column(Integer, primary_key=True)
    worksheet_id = Column(Integer, primary_key=True)


if __name__ == '__main__':
    bot = VkTools(access_token)
    params = bot.get_profile_info(789657038)
    users = bot.search_users(params)
    print(bot.get_photos(users[2]['id']))
