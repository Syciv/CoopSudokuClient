import json
from websocket import create_connection


class WebSocketClient:
    def __init__(self, room_id, server):
        self.server = server
        self.connection = create_connection('ws://' + server + '/room/' + room_id)
        print('Подключено по вебсокету к ' + server)
        self.room_id = room_id

    """
    Отправка сообщения с координатами и значением изменённой клетки
    """
    def send(self, h, w, v):
        data = {'height': int(h), 'width': int(w), 'value': int(v)}
        self.connection.send(json.dumps(data))

    """
    Получение сообщения по веб-сокету
    """
    def recv(self):
        return self.connection.recv()
