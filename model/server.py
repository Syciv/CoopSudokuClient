import configparser
import json
import random
import urllib

from zeep import Client


class Server:

    def __init__(self):
        self.address = self.get_first()
        self.wsdl = 'http://' + self.address + '/ws/rooms.wsdl'

    """
    Поиск комнаты по серверам
    """
    def find_room_server(self, room_id):
        connected = False
        i = 0
        servers = self.get_services()
        while not connected and i < len(servers):
            try:
                wsdl = 'http://' + servers[i] + '/ws/rooms.wsdl'
                print(wsdl)
                client = Client(wsdl=wsdl)
                rooms = client.service.getRooms()
                print(rooms)
                if rooms is not None and room_id in rooms:
                    print('Найдена комната на ' + servers[i])
                    server = servers[i]
                    self.address = server
                    return server
            except Exception as e:
                print(e)
            i += 1

    """
    Выбор случайного из доступных серверов
    """
    def get_first(self):
        servers = self.get_services()
        self.address = random.choice(servers)
        print(self.address)
        return self.address

    """
    Получение списка доступных серверов через consul
    """
    def get_services(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        consul = config['CONSUL']['address']
        service = config['CONSUL']['service']

        response = urllib.request.urlopen(f'http://{consul}/v1/catalog/service/{service}')
        data = json.loads(response.read().decode('utf-8'))
        result = []
        for service in data:
            result.append(f'{service["Address"]}:{service["ServicePort"]}')
        return result

