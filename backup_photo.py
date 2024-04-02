import requests
from tqdm import tqdm
import json

# Функция для получения фотографий пользователя из VK
def get_photos_from_vk(user_id, access_token):
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1,
        'photo_sizes': 1,
        'v': '5.131',
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'response' in data:
        return data['response']['items']
    else:
        print("Error:", data)
        return None

# Функция для загрузки фотографии на Яндекс.Диск
def upload_to_yadisk(token, photo_url, file_name):
    url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {
        'Authorization': 'OAuth ' + token
    }
    params = {
        'path': f'/VK_Photos/{file_name}',
        'url': photo_url
    }
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 202:
        print(f"Photo '{file_name}' uploaded successfully to Yandex.Disk")
    else:
        print(f"Error uploading photo '{file_name}' to Yandex.Disk:", response.text)

# Функция для сохранения информации о фотографиях в JSON-файл
def save_to_json(data):
    with open('photos_info.json', 'w') as f:
        json.dump(data, f, indent=4)

def main():
    # Запрос данных у пользователя
    user_id = input("Введите ID пользователя VK: ")
    vk_token = input("Введите токен VK: ")
    yadisk_token = input("Введите токен Яндекс.Диска: ")

    # Получение фотографий пользователя из VK
    photos = get_photos_from_vk(user_id, vk_token)

    if photos:
        # Создание папки на Яндекс.Диске
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {
            'Authorization': 'OAuth ' + yadisk_token
        }
        params = {
            'path': '/VK_Photos'
        }
        response = requests.put(url, headers=headers, params=params)
        if response.status_code == 201:
            print("Folder 'VK_Photos' created on Yandex.Disk")
        elif response.status_code == 409:
            print("Folder 'VK_Photos' already exists on Yandex.Disk")
        else:
            print("Error creating folder 'VK_Photos' on Yandex.Disk:", response.text)

        # Загрузка фотографий на Яндекс.Диск
        photos_info = []
        for photo in tqdm(photos, desc='Uploading photos to Yandex.Disk'):
            max_size_photo = max(photo['sizes'], key=lambda x: x['height']*x['width'])
            photo_url = max_size_photo['url']
            file_name = f"{photo['likes']['count']}.jpg"
            upload_to_yadisk(yadisk_token, photo_url, file_name)
            photos_info.append({
                'file_name': file_name,
                'size': {'width': max_size_photo['width'], 'height': max_size_photo['height']},
                'photo_url': photo_url
            })

        # Сохранение информации о фотографиях в JSON-файл
        save_to_json(photos_info)
    else:
        print("Не удалось получить фотографии пользователя из VK.")

if __name__ == "__main__":
    main()