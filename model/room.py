from zeep import Client


class Room:

    def __init__(self, server):
        self.room_id = None
        self.wsdl = 'http://' + server + '/ws/rooms.wsdl'
        self.client = Client(wsdl=self.wsdl)
        print('Адрес новой комнаты: ' + server)

    """
    Создание комнаты на выбранном сервере
    Возвращает id комнаты
    """
    def create_room(self, difficulty):
        self.room_id = self.client.service.createRoom({
            'difficulty': difficulty,
            'max': 3
        })
        return self.room_id

    """
    Получение состояния комнаты по её id
    """
    def fetch_room(self, room_id):
        self.room_id = room_id
        return self.client.service.fetchRoom(self.room_id)
