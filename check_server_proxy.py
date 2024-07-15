import requests
from proxy import get_proxies

hostname = 'http://minfin.gov.ru'

try:
    proxies = get_proxies()
    response = requests.get(hostname, proxies=proxies, timeout=30)
    if response.status_code == 200:
        print("Сервер доступен.")
    else:
        print(f"Сервер недоступен. Код состояния: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Не удалось подключиться к серверу. Ошибка: {e}")