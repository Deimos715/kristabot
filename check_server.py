import socket

hostname = 'minfin.gov.ru'
port = 443

try:
    socket.create_connection((hostname, port), timeout=10)
    print("Сервер доступен.")
except socket.error:
    print("Не удалось подключиться к серверу.")