#!/bin/python3
# -*- coding: utf-8 -*-

AskPwd__auth = 'Lasercata'
AskPwd__ver = '1.2'
AskPwd__last_update = '01.06.2021'

##-import
import sys

try:
    from Languages.lang import translate as tr
    from modules.hashes.hasher import Hasher

except ModuleNotFoundError as ept:
    print('\nPut the module' + ' ' + str(ept).strip('No module named') + ' back !!!')
    sys.exit()
    # tr = lambda t: t #This is just to test.

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QComboBox, QStyleFactory,
    QLabel, QGridLayout, QLineEdit, QMessageBox, QWidget, QPushButton, QCheckBox,
    QHBoxLayout, QGroupBox, QDialog)


##-main
class AskPwd(QDialog):
    '''Define a dialog which ask for a passord'''

    def __init__(self, title=tr('File password') + ' — Typt', parent=None):
        '''Create the GUI to ask password.'''

        #------ini
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('Style/Typt_logo.ico'))

        #------widgets
        #---main widget
        main_lay = QGridLayout()
        self.setLayout(main_lay)

        #---label
        main_lay.addWidget(QLabel(tr('Password :')), 0, 0)

        #---pwd_entry
        self.pwd = QLineEdit()
        self.pwd.setMinimumSize(QSize(200, 0))
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.returnPressed.connect(self.send) # Don't need to press the button : press <enter>

        main_lay.addWidget(self.pwd, 0, 1)

        #---check box
        self.inp_show = QCheckBox(tr('Show password'))
        self.inp_show.toggled.connect(self._show_pwd)

        main_lay.addWidget(self.inp_show, 1, 0, 1, 2, alignment=Qt.AlignCenter | Qt.AlignTop)

        #---button
        self.bt_get = QPushButton('>')
        self.bt_get.setMaximumSize(QSize(40, 50))
        self.bt_get.clicked.connect(self.send)

        main_lay.addWidget(self.bt_get, 0, 2)

        self.clear_pwd = None
        self.pwd_hashed = None

    def _show_pwd(self):
        '''Show the password or not. Connected with the checkbutton "inp_show"'''

        if self.inp_show.isChecked():
            self.pwd.setEchoMode(QLineEdit.Normal)

        else:
            self.pwd.setEchoMode(QLineEdit.Password)


    def send(self):
        '''Activated when <enter> pressed or when the button is clicked.'''

        text = self.pwd.text()
        self.pwd_hashed = Hasher('sha256').hash(Hasher('SecHash').hash(text))

        self.clear_pwd = text

        try:
            self.func(self.pwd_hashed)
        except AttributeError:
            pass

        self.close()


    def connect(self, function):
        '''
        Call `function` when enter pressed.

        - function : a function that takes one argument, the text that will be returned.
        '''

        self.func = function


    def use(parent=None):
        '''Use this function to launch the window. Return the word entered in the window.'''

        dlg = AskPwd(parent=parent)
        dlg.exec_()

        return dlg.pwd_hashed


class SetPwd(QDialog):
    '''Define a dialog that ask to set a password'''

    def __init__(self, title=tr('Set password') + ' — Typt', parent=None):
        '''Create the GUI to set a password.'''

        #------ini
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('Style/Typt_logo.ico'))

        #------widgets
        #---main widget
        main_lay = QGridLayout()
        self.setLayout(main_lay)

        self.clear_pwd = None
        self.pwd_hashed = None

        #-pwd1
        main_lay.addWidget(QLabel(tr('Password :')), 0, 0)

        self.pwd1_ledit = QLineEdit()
        self.pwd1_ledit.setMinimumSize(200, 0)
        self.pwd1_ledit.setEchoMode(QLineEdit.Password)
        main_lay.addWidget(self.pwd1_ledit, 0, 1, 1, 2)

        #-pwd2
        main_lay.addWidget(QLabel(tr('Confirm :')), 1, 0)

        self.pwd2_ledit = QLineEdit()
        self.pwd2_ledit.setEchoMode(QLineEdit.Password)
        #self.pwd2_ledit.returnPressed.connect(self.send)
        main_lay.addWidget(self.pwd2_ledit, 1, 1, 1, 2)

        #-pwd1 show
        self.pwd1_show = QCheckBox()
        self.pwd1_show.toggled.connect(self._show_pwd)
        main_lay.addWidget(self.pwd1_show, 0, 3)

        #-pwd2 show
        self.pwd2_show = QCheckBox()
        self.pwd2_show.toggled.connect(self._show_pwd)
        main_lay.addWidget(self.pwd2_show, 1, 3)

        self.dct_cb = {
            self.pwd1_show: self.pwd1_ledit,
            self.pwd2_show: self.pwd2_ledit
        }

        #---Buttons
        self.bt_ok = QPushButton('Ok')
        self.bt_ok.clicked.connect(self.send)
        main_lay.addWidget(self.bt_ok, 2, 2)

        self.bt_cancel = QPushButton('Cancel')
        self.bt_cancel.clicked.connect(self.close)
        main_lay.addWidget(self.bt_cancel, 2, 1)


    def _show_pwd(self):
        '''Actualise if the password needs to be shown.'''

        for k in self.dct_cb:
            if k.isChecked():
                self.dct_cb[k].setEchoMode(QLineEdit.Normal)

            else:
                self.dct_cb[k].setEchoMode(QLineEdit.Password)


    def send(self):
        '''Activated when <enter> pressed or when the button is clicked.'''

        text = self.pwd1_ledit.text()

        if text != self.pwd2_ledit.text():
            QMessageBox.critical(self, '!!! Wrong passwords !!!', '<h2>' + tr('The passwords does not correspond !') + '</h2>')
            return -3

        elif text == '':
            QMessageBox.critical(self, '!!! Empty passwords !!!', '<h2>{}</h2>'.format(tr('Please fill the two passwords fields.')))
            return -3

        self.pwd_hashed = Hasher('sha256').hash(Hasher('SecHash').hash(text))
        self.clear_pwd = text

        try:
            self.func(self.pwd_hashed)
        except AttributeError:
            pass

        self.close()


    def connect(self, function):
        '''
        Call `function` when enter pressed.

        - function : a function that takes one argument, the text that will be returned.
        '''

        self.func = function


    def use(title=tr('Set password') + ' — Typt', parent=None):
        '''Use this function to launch the window. Return the word entered in the window.'''

        dlg = SetPwd(title, parent=parent)
        dlg.exec_()

        return dlg.pwd_hashed


##-test
if __name__ == '__main__':

    class Test(QWidget):

        def __init__(self, parent=None):
            super().__init__(parent)

            self.setWindowTitle('Test')
            self.resize(500, 500)

            lay = QGridLayout()
            self.setLayout(lay)

            bt = QPushButton('AskPwd')
            bt.clicked.connect(self.test)
            lay.addWidget(bt)

            bt_2 = QPushButton('SetPwd')
            bt_2.clicked.connect(self.test_2)
            lay.addWidget(bt_2, 1, 0)


        def test(self):
            pwd = AskPwd.use()
            print(pwd)

        def test_2(self):
            pwd = SetPwd.use()
            print(pwd)

        def show_pwd(self, pwd):
            print(pwd)


    app = QApplication(sys.argv)

    win = Test()
    win.show()

    # w = AskPwd()
    # w.connect(lambda t: print(t))
    # w.show()

    app.exec_()
