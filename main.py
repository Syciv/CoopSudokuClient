import json

from PyQt5 import QtWidgets, uic, QtCore
import sys

from PyQt5.QtGui import QTextCursor

from model.connection import WebSocketClient
from model.room import Room
from model.server import Server

client = None


class ListenThread(QtCore.QThread):

    data_received = QtCore.pyqtSignal(int, int, int)

    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent=parent)

    """
    Функция выполнения потока слушания сообщений и изменения полей
    """
    def run(self):
        connected = True
        while connected:
            try:
                message = client.recv()
                data = json.loads(message)
                h = data['height']
                w = data['width']
                v = data['value']
                self.data_received.emit(h, w, v)
            except Exception as e:
                print(e)
                connected = False


class MyTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent, message_label):
        super(MyTextEdit, self).__init__(parent)
        self.textChanged.connect(self.handle_text_changed)
        self.message_label = message_label

    """
    Обработчик изменения текстового поля
    Отсылает новое изменение на сервер
    """
    def handle_text_changed(self):
        self.blockSignals(True)
        text = self.toPlainText()
        t = self.toPlainText()
        if len(text) > 0:
            if text[-1] not in '0123456789':
                self.setText('')
                t = ''
        if len(text) > 1:
            self.setText(text[-1])
            t = text[-1]

        name = self.objectName()
        h = name[4]
        w = name[6]
        v = 0 if len(t) == 0 else int(t)
        try:
            client.send(h, w, v)
        except Exception as e:
            print(e)
            self.message_label.setText('Произошла ошибка, создайте новую комнату')
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        self.blockSignals(False)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.sudoku_edits = []
        self.room = None
        self.server = None
        self.listen_thread = None
        self.message_label = self.findChild(QtWidgets.QLabel, 'message_label')

        uic.loadUi('sudoku.ui', self)

        self.grid = self.findChild(QtWidgets.QGridLayout, 'gridLayout')
        self.field = []
        self.init_field()
        self.create_button = self.findChild(QtWidgets.QPushButton, 'create_button')
        self.create_button.clicked.connect(self.create_button_click)
        self.connect_button = self.findChild(QtWidgets.QPushButton, 'connect_button')
        self.connect_button.clicked.connect(self.connect_button_click)
        self.difficulty = self.findChild(QtWidgets.QSpinBox, 'difficultySpinBox')
        self.room_id_edit = self.findChild(QtWidgets.QTextEdit, 'room_id_edit')
        self.show()

    """
    Инициализация поля - для каждой клеточки создаётся MyTextEdit
    с заданным обработчиком изменеия текта
    """
    def init_field(self):
        self.sudoku_edits = []
        normal_i = 0
        normal_j = 0
        for i in range(11):
            self.field.append([])
            if i == 3 or i == 7:
                widget = QtWidgets.QLabel()
                widget.setFixedSize(5, 5)
                self.grid.addWidget(widget, i, 0, 1, 1)
            else:
                for j in range(11):
                    if j == 3 or j == 7:
                        widget = QtWidgets.QLabel()
                        widget.setFixedSize(5, 5)
                        self.grid.addWidget(widget, i, j, 1, 1)
                    else:
                        edit = MyTextEdit(self, self.message_label)
                        edit.setObjectName('edit' + str(normal_i) + '_' + str(normal_j))
                        edit.setFixedSize(30, 30)
                        self.grid.addWidget(edit, i, j, 1, 1)
                        self.sudoku_edits.append(edit)
                        normal_j += 1
                normal_j = 0
                normal_i += 1
    """
    Нажатие на кнопку подключения
    """
    def create_button_click(self):
        self.server = Server()
        self.room = Room(self.server.address)
        difficulty = self.difficulty.value()
        room_id = self.room.create_room(difficulty)
        self.message_label.setText('Создана комната ' + room_id)
        print(self.room_id_edit)
        self.room_id_edit.setText(room_id)

    """
    Нажатие на кнопку подключения
    """
    def connect_button_click(self):
        try:
            self.server = Server()
            self.room = Room(self.server.address)
            print(self.room)
            room_id = self.room_id_edit.toPlainText()
            websocket_address = self.server.find_room_server(room_id)
            state = self.room.fetch_room(room_id)
            self.set_state(state['field'])
            self.message_label.setText('Подключено к комнате ' + room_id)

            global client
            client = WebSocketClient(room_id,  websocket_address)
            listener = ListenThread(self)
            listener.data_received.connect(self.set_value)
            listener.start()
        except Exception as e:
            print(e)

    """
    Установка состояния полученного поля
    """
    def set_state(self, state):
        for i in range(len(state)):
            self.sudoku_edits[i].blockSignals(True)
            if state[i] == '0':
                num = ''
            else:
                num = state[i]
            self.sudoku_edits[i].setText(num)
            self.sudoku_edits[i].blockSignals(False)

    """
    Установка значния в поле по координатам
    """
    def set_value(self, h, w, v):
        self.sudoku_edits[h * 9 + w].blockSignals(True)
        if v == 0:
            v = ''
        self.sudoku_edits[h * 9 + w].setText(str(v))
        self.sudoku_edits[h * 9 + w].blockSignals(False)


sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
