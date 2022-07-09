import requests
import json
import time
from pprint import pprint
from tqdm import tqdm

pprint("Добро пожаловать в программу резервного копирования фотографий (аватарок) из профиля пользователя социальной сети Вконтакте в облачное хранилище Яндекс.Диск! Для дальнейшего взаимодействия с программой и проверки ее работоспособности, пожалуйста, подготовьте Ваши токены с Полигона Яндекс.Диска и ВКонтакте, потому что без них вообще ничего не заработает:(  ")
tokenVK = input("Введите Ваш токен Вконтакте: ")
tokenYaDisk = input("Введите Ваш токен с Полигона Яндекс.Диска: ")

url_ya_poligon = 'https://cloud-api.yandex.net/v1/disk/resources'
url_yad = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'OAuth {tokenYaDisk}'}


def get_all_profiles_photos(): #Шаг1.
    '''Запрос к ВК и получение ответа с данными'''
    data_from_VK = requests.get("https://api.vk.com/method/photos.get?v=5.131", params={"access_token": tokenVK,
                                                                             "album_id": "profile",
                                                                             "extended": 1,
                                                                             "photo_sizes": 1,
                                                                             "count": 8})
    return data_from_VK.json()



def json_file_creation(data): #Шаг2.
    '''Получение на вход результата функции get_all_profiles_photos и создание json файла'''
    with open("Function get_all_profiles_photos Result. Json", "w") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

json_file_creation(get_all_profiles_photos())



def get_maximum_resolution_photo(size_dict): #Шаг4
    '''Получение данных от функции get_maxSize_date_names_json и выбор фото в максимальном разрешении'''
    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    else:
        return size_dict['height']
    


def create_folder(path): #Шаг6
    """Создание папки на Яндекс.Диске"""
    requests.put(f'{url_ya_poligon}?path={path}', headers=headers)

create_folder('BackUp from VK') # Передаем в функцию create_folder название папки



def upload_pics_to_ya_disk(naming, URL_pics): #Шаг7
    '''Загрузка картинок в Яндекс.Диск'''
    requests.post(url_yad, headers=headers, params={'url': f'{URL_pics}', 'path': f"/BackUp from VK/ {naming}"})
    for i in tqdm(range(1)): #прогресс бар
        time.sleep(1)



def get_maxSize_date_names_json(dict_second_level): #Шаг3
    '''Работа с данными, полученными от ВК из файла Function get_all_profiles_photos Result. Json'''
    l_photos = []
    list_photos = []
    like = []
    for item in dict_second_level['items']:

        dict_third_level = item['sizes']
        max_sizes = max(dict_third_level, key=get_maximum_resolution_photo)
        max_sizes_url = max(dict_third_level, key=get_maximum_resolution_photo)['url'] #Получение списка ссылок на фото в максимальном разрешении
        pprint(max_sizes_url)
        max_sizes_type = max(dict_third_level, key=get_maximum_resolution_photo)['type'] #Для передачи в Json файл Получаем список типов размеров фото в максимальном разрешении

        # Преобразуем дату в удобный для восприятия вид
        t = item['date']
        t1 = time.ctime(t)
        ts = time.strptime(t1)
        date_time = time.strftime("%Y-%m-%d %H_%M_%S", ts)

        # Реализация требования Курсового проекта по присвоению имен фотографиям(likes или likes+date)
        p_likes = item['likes']['count']
        if p_likes not in like:
            l_photos.append({'Name': str(p_likes) + '.jpg', 'Likes': str(p_likes), 'Date': date_time})
            list_photos.append({"file_name": str(p_likes) + '.jpg', "size": max_sizes_type})
        else:
            l_photos.append(
                {'Name': str(p_likes) + "_" + date_time + '.jpg', 'Likes': str(p_likes), 'Date': date_time})
            list_photos.append({"file_name": str(p_likes) + "_" + date_time + '.jpg', "size": max_sizes_type})
        like.append(p_likes)

        # Создание Json файла с именем и размером (а точнее типом размера) фото
        with open('photos.json', 'w') as f:
            json.dump(list_photos, f, indent=2, ensure_ascii=False)

        # Получение имени файла
        for photo in l_photos:
            photo_names = str(photo['Name'])

        # Передаем в функцию upload_pics_to_ya_disk имена и ссылки на фото в максимальном разрешении
        upload_pics_to_ya_disk(photo_names, max_sizes_url)

dict_first_level = json.load(open("Function get_all_profiles_photos Result. Json"))["response"]
get_maxSize_date_names_json(dict_first_level)



if __name__ == "__main__":
    get_all_profiles_photos()