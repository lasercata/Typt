#!/bin/python3
# -*- coding: utf-8 -*-

'''Launch Typt with PyQt5 graphical interface.'''

Typt_gui__auth = 'Lasercata'
Typt_gui__last_update = '30.05.2021'
Typt_gui__version = '1.2'


##-import
#from modules.base.ini import *
#---------packages
#------gui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QCloseEvent, QPalette, QColor, QFont, QKeySequence
from PyQt5.QtWidgets import (QApplication, QMainWindow, QComboBox, QStyleFactory,
    QLabel, QGridLayout, QLineEdit, QMessageBox, QWidget, QPushButton, QCheckBox,
    QHBoxLayout, QVBoxLayout, QGroupBox, QTabWidget, QTableWidget, QFileDialog,
    QRadioButton, QTextEdit, QButtonGroup, QSizePolicy, QSpinBox, QFormLayout,
    QSlider, QMenuBar, QMenu, QPlainTextEdit, QAction, QToolBar, QShortcut, QDialog)

#------other
from os import chdir, getcwd
from os.path import isfile, expanduser
from shutil import copy
import sys

from ast import literal_eval #safer than eval

import webbrowser #Open web page (in About)

#---------Typt modules
try:

    from Languages.lang import translate as tr
    from Languages.lang import langs_lst, lang

    from modules.base.base_functions import *
    from modules.base.progress_bars import *
    from modules.base.AskPwd import AskPwd, SetPwd

    from modules.base.gui.GuiStyle import GuiStyle
    from modules.base.gui.Popup import Popup

    from modules.hashes import hasher
    from modules.AES import AES

except ModuleNotFoundError as ept:
    err = str(ept).strip("No module named")

    try:
        cl_out(c_error, tr('Put the module {} back !!!').format(err))

    except NameError:
        try:
            print('\n' + tr('Put the module {} back !!!').format(err))

        except NameError:
            print('\n' + 'Put the module {} back !!!'.format(err))

    sys.exit()


##-ini
#---------version
try:
    with open('version.txt', 'r') as f:
        Typt_version_0 = f.read()
    Typt_version = ""
    for k in Typt_version_0:
        if not ord(k) in (10, 13):
            Typt_version += k

except FileNotFoundError:
    cl_out(c_error, tr('The file "version.txt" was not found. A version will be set but can be wrong.'))
    Typt_version = '1.0.0 ?'

else:
    if len(Typt_version) > 16:
        cl_out(c_error, tr('The file "version.txt" contain more than 16 characters, so it certainly doesn\'t contain the actual version. A version will be set but can be wrong.'))
        Typt_version = '1.0.0 ?'


#---------Useful lists/dicts
lst_encod = ('utf-8', 'ascii', 'latin-1')



##-GUI
class TyptGui(QMainWindow):
    '''Class defining Typt' graphical user interface using PyQt5'''

    def __init__(self, files=[], parent=None):
        '''
        Create the window

        - files : list of str. Try to open the files in tabs. If empty, open a new tab.
        '''

        #------ini
        super().__init__(parent)
        self.setWindowTitle('Untitled — Typt v' + Typt_version)
        self.setWindowIcon(QIcon('Style/Typt_logo.ico'))

        #self.style = style_test
        self.app_style = GuiStyle()
        self.style = self.app_style.style_sheet

        #------Widgets
        #---Central widget
        self.main_wid = QTabWidget()
        # self.main_wid.setTabPosition(QTabWidget.South)
        # self.main_wid.setMovable(True) #Todo: moving the tab change its index, => all list are wrong then.
        self.main_wid.setTabsClosable(True)
        self.main_wid.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.main_wid)

        #Todo: movable tabs ? it changes the index => all lists are wrong.

        self.save_path = expanduser('~')
        self.open_path = expanduser('~')


        #---font
        self.fixed_font = QFont('monospace')
        self.fixed_font.setStyleHint(QFont.TypeWriter)

        #---Lists
        self.tabs = [] #List of TextDrop #QPlainTextEdit
        self.saved = [] #List of bool (or None if not modified)
        self.filenames = [] #List of str, the filenames.
        self.tab_names = [] #List of str, the filename without the path.
        self.passwords = [] #List of str, the files passwords. None if not set.

        #---Statusbar
        self._create_statusbar()

        #---Menu
        self._create_menu_bar()

        # QShortcut('Ctrl+T', self).activated.connect(lambda: print(self.current_tab))

        #------Show
        self.show()
        self.resize(1100, 600)

        self.current_tab = 0

        if len(files) == 0:
            self.new() #Create first tab

        else:
            for fn in files:
                self.open(fn)

        self._chk_tab(len(files) - 1)
        self.main_wid.currentChanged.connect(self._chk_tab)

        self.new()
        self._close_tab(len(self.tabs) - 1, False)



    def _create_menu_bar(self):
        '''Create the menu bar.'''

        #------Menu
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        #------The menus
        #---File
        self.file_m = menu_bar.addMenu(tr('&File'))

        #-New
        self.new_ac = QAction(tr('&New'), self)
        self.new_ac.setShortcut('Ctrl+N')
        self.new_ac.triggered.connect(lambda: self.new())
        self.file_m.addAction(self.new_ac)

        self.file_m.addSeparator()

        #-Open
        self.open_ac = QAction(tr('&Open ...'), self)
        self.open_ac.setShortcut('Ctrl+O')
        self.open_ac.triggered.connect(self.open)
        self.file_m.addAction(self.open_ac)

        #-Open
        self.open_recent_m = QMenu(tr('Open &Recent'), self)
        self.op_rec_dct = {}
        self.file_m.addMenu(self.open_recent_m)

        self.file_m.addSeparator()

        #-Save
        self.save_ac = QAction(tr('&Save'), self)
        self.save_ac.setShortcut('Ctrl+S')
        self.save_ac.triggered.connect(self.save)
        #self.save_ac.setStatusTip("Save editor's text in a file")
        self.file_m.addAction(self.save_ac)

        #-Save As
        self.save_as_ac = QAction(tr('Save &As'), self)
        self.save_as_ac.setShortcut('Ctrl+Shift+S')
        self.save_as_ac.triggered.connect(lambda: self.save(as_=True))
        self.file_m.addAction(self.save_as_ac)

        self.file_m.addSeparator()

        self.close_tab_ac = QAction('&' + tr('Close', self))
        self.close_tab_ac.setShortcut('Ctrl+W')
        self.close_tab_ac.triggered.connect(lambda: self._close_tab(self.current_tab))
        self.file_m.addAction(self.close_tab_ac)

        self.file_m.addSeparator()

        #-Exit
        self.exit_ac = QAction(tr('&Quit'), self)
        self.exit_ac.setShortcut('Ctrl+Q')
        self.exit_ac.triggered.connect(self.quit)
        self.file_m.addAction(self.exit_ac)


        #---Edit
        self.edit_m = menu_bar.addMenu(tr('&Edit'))

        #-Undo
        self.undo_ac = QAction(tr('&Undo'), self)
        self.undo_ac.setEnabled(False)
        self.undo_ac.setShortcut('Ctrl+Z')
        self.undo_ac.triggered.connect(lambda: self.tabs[self.current_tab].undo())
        self.edit_m.addAction(self.undo_ac)

        #-Redo
        self.redo_ac = QAction(tr('Re&do'), self)
        self.redo_ac.setEnabled(False)
        self.redo_ac.setShortcut('Ctrl+Shift+Z')
        self.redo_ac.triggered.connect(lambda: self.tabs[self.current_tab].redo())
        self.edit_m.addAction(self.redo_ac)

        self.edit_m.addSeparator()

        #-Cut
        self.cut_ac = QAction(tr('&Cut'), self)
        self.cut_ac.setShortcut('Ctrl+X')
        self.cut_ac.triggered.connect(lambda: self.tabs[self.current_tab].cut())
        self.edit_m.addAction(self.cut_ac)

        #-Copy
        self.copy_ac = QAction(tr('&Copy'), self)
        self.copy_ac.setShortcut('Ctrl+C')
        self.copy_ac.triggered.connect(lambda: self.tabs[self.current_tab].copy())
        self.edit_m.addAction(self.copy_ac)

        #-Paste
        self.paste_ac = QAction(tr('&Paste'), self)
        self.paste_ac.setShortcut('Ctrl+V')
        self.paste_ac.triggered.connect(lambda: self.tabs[self.current_tab].paste())
        self.edit_m.addAction(self.paste_ac)

        #-Delete
        #self.del_ac = QAction(tr('De&lete'), self)
        #self.del_ac.setShortcut(QKeySequence.Delete)
        #self.del_ac.triggered.connect(lambda: self.tabs[self.current_tab].del_())
        #Todo : correct this line : del_ method is not defined for QPlainTextEdit widget whereas it is defined for QTextEdit widget
        #self.edit_m.addAction(self.del_ac)

        #-Select all
        self.sa_ac = QAction(tr('Sele&ct all'), self)
        self.sa_ac.setShortcut(QKeySequence.SelectAll)
        self.sa_ac.triggered.connect(lambda: self.tabs[self.current_tab].selectAll())
        self.edit_m.addAction(self.sa_ac)


        #---View
        self.view_m = menu_bar.addMenu(tr('&View'))

        #-Resize original
        self.resize_ac = QAction(tr('&Resize to original size'), self)
        self.resize_ac.triggered.connect(lambda: self.resize(1100, 600))
        self.view_m.addAction(self.resize_ac)


        #---Encryption
        self.encryption_m = menu_bar.addMenu(tr('E&ncryption'))

        #-Change password
        self.set_pwd_ac = QAction(tr('&Set Password'), self)
        self.set_pwd_ac.setEnabled(True)
        #self.set_pwd_ac.setShortcut('Ctrl+Z')
        self.set_pwd_ac.triggered.connect(self.set_pwd)
        self.encryption_m.addAction(self.set_pwd_ac)

        #-Change password
        self.ch_pwd_ac = QAction(tr('&Change Password'), self)
        self.ch_pwd_ac.setEnabled(False)
        #self.ch_pwd_ac.setShortcut('Ctrl+Z')
        self.ch_pwd_ac.triggered.connect(self.ch_pwd)
        self.encryption_m.addAction(self.ch_pwd_ac)

        #---Settings
        self.settings_m = menu_bar.addMenu(tr('&Settings'))

        #-Theme
        self.theme_m = QMenu(tr('Color &Scheme'), self)
        self.settings_m.addMenu(self.theme_m)

        #-Themes
        self.style_dct = {}
        for k in self.app_style.main_styles:
            self.style_dct[k] = QAction(k, self)
            self.style_dct[k].triggered.connect(self._set_style) #lambda: self.app_style.set_style(k))
            self.theme_m.addAction(self.style_dct[k])

        self.settings_m.addSeparator()

        #-Configure Typt
        self.config_ac = QAction(tr('&Configure Typt ...'), self)
        self.config_ac.setShortcut('Ctrl+R')
        self.config_ac.triggered.connect(lambda: SettingsWin.use(self.style, self.app_style, parent=self))
        self.settings_m.addAction(self.config_ac)


        #---Help
        self.help_m = menu_bar.addMenu(tr('&Help'))

        #-About
        self.about_ac = QAction(tr('&About'), self)
        self.about_ac.setShortcut('Shift+F1')
        self.about_ac.triggered.connect(self.show_about)
        self.help_m.addAction(self.about_ac)


    def _create_statusbar(self):
        '''Create the status bar.'''

        self.statusbar = self.statusBar()

        #Todo: add a label showing if password is set ?

        #------Widgets
        #---Words count
        self.wc_lb = QLabel()
        self.statusbar.addPermanentWidget(self.wc_lb)

        self.statusbar.addPermanentWidget(QLabel('  ')) #Spacing

        #---Saved
        self.saved_lb = QLabel()
        self.statusbar.addPermanentWidget(self.saved_lb)

        self.statusbar.addPermanentWidget(QLabel('  ')) #Spacing

        #---Password
        self.pwd_set_lb = QLabel()
        self.statusbar.addPermanentWidget(self.pwd_set_lb)

        self.statusbar.addPermanentWidget(QLabel('  ')) #Spacing

        #---Encoding
        self.encod_box = QComboBox()
        self.encod_box.addItems(lst_encod)
        self.statusbar.addPermanentWidget(self.encod_box)



    def _close_tab(self, tab_ind, new=True):
        '''
        Close the tab #`tab_ind`, after check if txt saved.

        - tab_ind : the tab index ;
        - a bool indicating if creating a new tab if there is not.
        '''

        if self._msg_box_save(tab_ind, tr('Close tab') + ' — Typt'):
            self.main_wid.removeTab(tab_ind)
            del self.tabs[tab_ind]
            del self.saved[tab_ind]
            del self.filenames[tab_ind]
            del self.tab_names[tab_ind]
            del self.passwords[tab_ind]

        if len(self.tabs) == 0 and new:
            self.new()

        self._chk_tab(len(self.tabs)-1)


    def _chk_tab(self, tab):
        '''Set `self.current_tab` to `tab`, change window title, word count, and the saved label.'''

        self.current_tab = tab

        self._show_wc(tab)

        try:
            self.setWindowTitle('{} — Typt v{}'.format(self.tab_names[tab], Typt_version))
            self._set_save_lb_txt()

        except IndexError as err:
            print('Typt: TyptGui._chk_tab: line approx 365: {}'.format(err))

        self.set_pwd_ac.setEnabled(self.passwords[tab] == None)
        self.ch_pwd_ac.setEnabled(self.passwords[tab] != None)


    def _set_style(self, a=False):
        '''Used with the menu to set the style.'''

        self.app_style.set_style(self.sender().text())


    def _get_word_count(self, txt):
        '''Return the number of characters and the number of words which are `txt`.'''

        if txt == '':
            return 0, 0, 0

        cc = len(txt) # Characters count
        gcc = 0 # Graphic characters count
        for k in txt:
            if ord(k) >= 32 and ord(k) != 127:
                gcc += 1
        wc = len(txt.replace('\n', ' ').split()) # Words count (may not be accurate, ';' will be counted as a word for example).

        return cc, gcc, wc

    def _show_wc(self, tab_ind=None):
        '''
        Show the word count in the status bar.

        - tab_ind : the tab index. if None, read text from self.sender().
        '''

        if tab_ind == None:
            txt = self.sender().toPlainText()

        else:
            txt = self.tabs[tab_ind].toPlainText()

        cc, gcc, wc = self._get_word_count(txt)
        self.wc_lb.setText(tr('{} words, {} chars, {} gchars').format(format(wc, '_').replace('_', ' '), format(cc, '_').replace('_', ' '), format(gcc, '_').replace('_', ' ')))


    def _set_save_lb_txt(self):
        '''Set the correct text to self.save_lb.'''

        if self.saved[self.current_tab]:
            self.saved_lb.setText(tr('Saved'))
            self.saved_lb.setStyleSheet('color: #0f0')

            self.setWindowTitle('{} — Typt v{}'.format(self.tab_names[self.current_tab], Typt_version))

        elif self.saved[self.current_tab] == None:
            self.saved_lb.setText('')

            self.setWindowTitle('{} — Typt v{}'.format(self.tab_names[self.current_tab], Typt_version))

        else:
            self.saved_lb.setText(tr('Unsaved'))
            self.saved_lb.setStyleSheet('color: #f00')

            self.setWindowTitle('{} * — Typt v{}'.format(self.tab_names[self.current_tab], Typt_version))

        if self.passwords[self.current_tab] == None:
            self.pwd_set_lb.setText(tr('No password'))
            self.pwd_set_lb.setStyleSheet('color: #f00')

        else:
            self.pwd_set_lb.setText(tr('Password set'))
            self.pwd_set_lb.setStyleSheet('color: #0f0')


    def _txt_changed(self):
        '''Set self.saved[tab_ind] to False. Called when signal 'textChanged' recieved.'''

        self.saved[self.current_tab] = False

        #Todo: count undos to set it to True if (nb_do - nb_undo) == 0 ?

        #------Set label
        self._set_save_lb_txt()


    def _msg_box_save(self, tab_ind=None, title='Quit Typt'):
        '''
        Check if there are things unsaved (text), and show a QMessageBox question.
        Return a bool indicating if continue (True) or not (False).

        - tab_ind : the tab index in the one check if there is unsaved text. If None, check in all ;
        - title : QMessageBox window's title.
        '''

        txt_ = False
        txt_tabs = []
        txt_ind = []

        if tab_ind == None:
            for index, t in enumerate(self.tabs):
                if self.saved[index] == False: #can be True, None, or False.
                    txt_tabs.append('"' + self.filenames[index].split('/')[-1] + '"')
                    txt_ind.append(index)
                    txt_ = True

        elif self.saved[tab_ind] == False:
            txt_tabs.append('"' + self.filenames[tab_ind].split('/')[-1] + '"')
            txt_ind.append(tab_ind)
            txt_ = True

        if txt_:
            if len(txt_tabs) == 1:
                msg = tr('The document') + ' ' + set_prompt(txt_tabs) + \
                ' ' + tr('has been modified.') + '\n' + tr('Do you want to save your changes or discard them ?')

            else:
                msg = tr('The documents') + ' ' + set_prompt(txt_tabs) + \
                ' ' + tr('have been modified.') + '\n' + tr('Do you want to save your changes or discard them ?')


            answer = QMessageBox.warning(self, title, msg, \
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if answer == QMessageBox.Cancel:
                return False

            elif answer == QMessageBox.Save:
                for k in txt_ind:
                    ret = self.save(k)

                if ret == -3:
                    return False #Canceled

        return True



    def new(self, fn=None):
        '''
        Create a new tab.

        - fn : the filename. If it is None, set it to 'Untitled (#)'.
        '''

        new_tab_ind = len(self.tabs)
        if new_tab_ind == 0 and fn == None:
            tab_name = 'Untitled'

        elif fn == None:
            k = new_tab_ind
            tab_name = f'Untitled ({new_tab_ind})'

            while tab_name in self.tab_names:
                k += 1
                tab_name = f'Untitled ({k})'

        else:
            tab_name = fn

        #-The lists
        self.saved.append(None) #Set to None: not modified
        self.filenames.append(tab_name) #Set filename
        self.passwords.append(None)

        f = tab_name.split('/')[-1]
        k = 0
        while f in self.tab_names:
            k += 1
            f = tab_name.split('/')[-1] + f' ({k})'

        self.tab_names.append(f)

        #-The tab
        self.tabs.append(TextDrop(self, self))
        self.tabs[new_tab_ind].setFont(self.fixed_font)
        self.tabs[new_tab_ind].textChanged.connect(self._show_wc)
        self.tabs[new_tab_ind].textChanged.connect(self._txt_changed)
        self.tabs[new_tab_ind].undoAvailable.connect(self.undo_ac.setEnabled) #Todo: if change tab, actualise these.
        self.tabs[new_tab_ind].redoAvailable.connect(self.redo_ac.setEnabled)
        self.main_wid.addTab(self.tabs[new_tab_ind], self.tab_names[-1])

        self.main_wid.setCurrentIndex(new_tab_ind)
        self.setWindowTitle('{} — Typt v{}'.format(self.tab_names[-1], Typt_version))


    def open(self, filename=False):
        '''
        Select, read, and set text from a file to `self.txt_in`.

        - filename : the filename, or False. If it is False, ask the user for it.

        Return :
            -1 if file not found ;
            -2 if encoding error ;
            None otherwise.
        '''

        if filename == False:
            fn = QFileDialog.getOpenFileName(self, tr('Open file') + ' — Typt', self.open_path, tr('Typt files(*.typt);;Text files(*.txt);;All files(*)'))[0]

            if fn in ((), ''):
                return -3 #Canceled

            else:
                self.open_path = '/'.join(fn.split('/')[:-1])

        else:
            fn = filename

        if fn not in self.op_rec_dct:
            f = fn.split('/')[-1]
            self.op_rec_dct[fn] = QAction('{} [{}]'.format(f, fn), self)
            self.op_rec_dct[fn].triggered.connect(lambda: self.open(fn))
            self.open_recent_m.addAction(self.op_rec_dct[fn])


        try:
            with open(fn, mode='rb') as f:
                file_content = f.read()

        except FileNotFoundError:
            QMessageBox.critical(None, '!!! ' + tr('Error') + ' !!!', '<h2>' + tr('The file was NOT found') + ' !!!</h2>')
            return -1 #stop


        if fn[-5:] == '.typt':
            while True:
                #---Ask password
                pwd = AskPwd.use(parent=self)

                if pwd == None:
                    return -3

                #---Decryption
                try:
                    f_dec = AES.AES(256, pwd, hexa=True).decryptText(file_content, mode_c='b', encoding=str(self.encod_box.currentText()))

                except UnicodeDecodeError:
                    QMessageBox.critical(None, '!!! Wrong password !!!', '<h2>{}</h2>'.format(tr('This is not the good password !')))

                except ValueError:
                    QMessageBox.critical(None, '!!! File error !!!', '<h2>{}</h2>'.format(tr('The file is not well formatted !')))
                    return -2

                else:
                    break

        else:
            try:
                f_dec = file_content.decode(encoding=str(self.encod_box.currentText()))

            except UnicodeDecodeError:
                QMessageBox.critical(None, '!!! ' + tr('Encoding error') + ' !!!', \
                    '<h2>' + tr('The file can\'t be decoded with this encoding') + '.</h2>')

                return -2 #stop

            pwd = None

        #---Remove 'Untitled' tab
        if len(self.tabs) == 1 and self.saved[0] == None:
            self._close_tab(0, new=False)

        #---Create a new tab
        self.new(fn)

        #---Set text
        self.tabs[-1].setPlainText(f_dec)
        # self.filenames[-1] = fn
        # self.tab_names[-1] = fn.split('/')[-1]
        self.saved[-1] = True
        self.passwords[-1] = pwd

        self.ch_pwd_ac.setEnabled(pwd != None)

        self._set_save_lb_txt()
        self.statusbar.showMessage('File opened !', 3000)


    def save(self, tab_ind=False, as_=False):
        '''
        Save text into a file.

        - tab_ind : The tab index. Used to choose from where read text to save it. If False, read current tab ;
        - as_ : a bool which indicates if clicked on 'Save' (True) or 'Save As' (False).

        Return -3 if canceled.
        '''

        #------Tests
        if as_ not in (True, False):
            raise ValueError('The argument `as_` is not a bool.')

        #------Get filename (fn) and text (txt)
        if tab_ind == False:
            tab_ind = self.current_tab

        txt = self.tabs[tab_ind].toPlainText()

        enc = True

        if 'Untitled' in self.filenames[tab_ind] or as_:
            fn = QFileDialog.getSaveFileName(self, tr('Save file') + ' — Typt', self.save_path, tr('Typt files(*.typt);;Text files(*.txt);;All files(*)'))[0]

            if fn[-5:] != '.typt' and self.passwords[tab_ind] == None:
                if QMessageBox.warning(self, '!!! Not Encrypted !!!', '<h2>' + tr('If you continue, the file will NOT be encrypted !') + '</h2>', QMessageBox.Cancel | QMessageBox.Ignore, QMessageBox.Cancel) == QMessageBox.Cancel:
                    return -3 #Aborted.

                else:
                    enc = False

            self.filenames[tab_ind] = fn

        else:
            fn = self.filenames[tab_ind]

            if fn[-5:] != '.typt' and self.passwords[tab_ind] == None:
                enc = False
                self.statusbar.showMessage(tr('Not encrypted !'), 3000)

        if fn in ((), ''):
            return -3 # Canceled

        else:
            self.save_path = '/'.join(fn.split('/')[:-1])

        #------Encrypt
        if self.passwords[tab_ind] == None and enc:
            self.passwords[tab_ind] = SetPwd.use(parent=self)

            if self.passwords[tab_ind] == None:
                return -3 #Abort

        #------Write
        try:
            if enc:
                txt_enc = AES.AES(256, self.passwords[tab_ind], hexa=True).encryptText(txt, mode_c='b', encoding=str(self.encod_box.currentText()))

            else:
                txt_enc = txt.encode(encoding=str(self.encod_box.currentText()))

            with open(fn, 'wb') as f:
                f.write(txt_enc)

        except UnicodeEncodeError:
            QMessageBox.critical(self, '!!! {} !!!'.format(tr('Encoding error')), '<h2>' + tr("The file can't be encoded with this encoding") + '</h2>')
            return -3

        self.saved[tab_ind] = True
        self.filenames[tab_ind] = fn
        self.tab_names[tab_ind] = fn.split('/')[-1]

        self._chk_tab(tab_ind)
        self.main_wid.setTabText(tab_ind, self.tab_names[tab_ind])

        self._set_save_lb_txt()
        self.statusbar.showMessage(tr('Saved') + ' !', 3000)



    def ch_pwd(self):
        '''Change the file's password'''

        tab_ind = self.current_tab

        # if self.passwords[tab_ind] == None:
        #     QMessageBox.critical(self, '!!! Not saved !!!', '<h2>' + tr('Please save the file before !') + '</h2>')

        while True:
            old_pwd = AskPwd.use(parent=self)

            if old_pwd == None:
                return -3 #Aborted

            elif old_pwd != self.passwords[tab_ind]:
                QMessageBox.critical(None, '!!! Wrong password !!!', '<h2>{}</h2>'.format(tr('This is not the good password !')))

            else:
                break

        new_pwd = SetPwd.use(tr('New password') + '— Typt', parent=self)

        if new_pwd == None:
            return -3 #Aborted

        self.passwords[tab_ind] = new_pwd

        #self.save(tab_ind)

        self._chk_tab(tab_ind)
        self.statusbar.showMessage(tr('Password changed !'), 3000)


    def set_pwd(self):
        '''Set the file's password'''

        tab_ind = self.current_tab

        new_pwd = SetPwd.use(tr('Password') + '— Typt', parent=self)

        if new_pwd == None:
            return -3 #Aborted

        self.passwords[tab_ind] = new_pwd

        self._chk_tab(tab_ind)
        self.statusbar.showMessage(tr('Password set !'), 3000)



    def show_about(self):
        '''Show the about popup.'''

        about = '<center><h1>Typt_v{}</h1></center>\n'.format(Typt_version)

        about += tr('Typt is a secure raw text editor that save text encrypted with the symetrical algorithm cipher AES-256-CBC. It manages multiples tabs.')

        about += '<h2>{}</h2>'.format(tr('Authors'))
        about += '<p>Lasercata (https://github.com/lasercata)</p>'
        about += '<p>Elerias (https://github.com/EleriasQueflunn)</p>'
        about += '<br>'
        about += '<p>{} : https://github.com/lasercata/Typt</p>'.format(tr('More information on the GitHub repository'))


        bt_repo = QPushButton('Open repo')
        bt_repo.clicked.connect(lambda: webbrowser.open_new_tab('https://github.com/lasercata/Typt'))

        p = Popup(bt_align='right', style=self.style, parent=self)
        p.main_lay.addWidget(bt_repo, 1, 0, Qt.AlignLeft)
        p.pop(tr('About') + ' — Typt', about, html=True)



    #---------quit
    def quit(self, event=None):
        '''Quit the application. Check if there is text unsaved, and ask confirmation if there is.'''

        global app

        if not self._msg_box_save():
            if event not in (None, True, False):
                event.ignore()
            return -3

        if event not in (None, True, False):
            event.accept()

        else:
            app.quit()


    def closeEvent(self, event=None):
        self.quit(event)


    #---------use
    def use(files=[]):
        '''Launch the application.'''

        global app, win

        app = QApplication(sys.argv)
        win = TyptGui(files)

        #---Show 'Ready' in status bar
        win.statusbar.showMessage(tr('Ready !'), 3000)

        win.tabs[-1].setFocus()

        sys.exit(app.exec_())



##-Widgets / windows
class TextDrop(QPlainTextEdit):
    '''Redifine the drop events to open the dropped file in a new tab.'''

    def __init__(self, win, parent=None):
        '''
        Initiate object.

        - win : the TyptGui object.
        '''

        super().__init__(parent)

        self.win = win
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        '''Check if file exists'''

        if isfile(e.mimeData().text()[7:]):
            e.accept()

        else:
            e.ignore()

    def dropEvent(self, e):
        '''Open new tab'''

        fn = e.mimeData().text()[7:]

        self.win.open(fn)


class SettingsWin(QDialog): #QMainWindow):
    '''Defining the Settings window.'''

    def __init__(self, style, app_style, parent=None):
        '''Initiate class'''

        #------Ini
        super().__init__(parent)
        self.setWindowTitle('Typt v' + Typt_version + ' | ' + tr('Settings'))
        self.setWindowIcon(QIcon('Style/Typt_logo.ico'))

        self.style = style
        self.app_style = app_style

        self._create_settings()


    def _create_settings(self):
        '''Create the widgets'''

        #------ini
        #tab_stng = QWidget()

        tab_stng_lay = QGridLayout()
        tab_stng_lay.setContentsMargins(5, 5, 5, 5)
        # tab_stng.setLayout(tab_stng_lay)
        self.setLayout(tab_stng_lay)

        #------widgets
        #---main style
        #-ini
        self.style_grp = QGroupBox('Style')
        self.style_grp.setMaximumSize(500, 100)
        #self.style_grp.setMinimumSize(500, 200)
        main_style_lay = QHBoxLayout()
        self.style_grp.setLayout(main_style_lay)
        tab_stng_lay.addWidget(self.style_grp, 0, 0, Qt.AlignLeft | Qt.AlignTop)

        self.main_style_palette = QApplication.palette()

        #-combo box
        main_style_lay.addWidget(QLabel('Style :'))

        self.stng_main_style_opt = QComboBox()
        self.stng_main_style_opt.addItems(self.app_style.main_styles)
        self.stng_main_style_opt.activated[str].connect(
            lambda s: self.app_style.set_style(s, self.main_style_std_chkb.isChecked())
        )
        self.stng_main_style_opt.setCurrentText(self.app_style.main_style_name)
        main_style_lay.addWidget(self.stng_main_style_opt)

        #-check box
        self.main_style_std_chkb = QCheckBox(tr("&Use style's standard palette"))
        self.main_style_std_chkb.setChecked(True)
        self.main_style_std_chkb.toggled.connect(
            lambda: self.app_style.set_style(
                self.stng_main_style_opt.currentText(),
                self.main_style_std_chkb.isChecked()
            )
        )
        main_style_lay.addWidget(self.main_style_std_chkb)


        #---Change language
        #-function
        def chg_lang():
            '''
            Changing the language (in the text file). The user need to
            close the app and relaunch it manually to apply the new lang.
            '''

            new_lang = self.stng_lang_box.currentText()

            #---test
            if new_lang == lang:
                return -3

            #---write
            with open('Data/lang.txt', 'w') as f:
                f.write(new_lang)

            #---close
            rep = QMessageBox.question(
                None, tr('Done !'),
                '<h2>' + tr('The new lang will apply the next time you launch Typt.') + '</h2>\n<h2>' + tr('Quit now ?') + '</h2>',
                QMessageBox.No | QMessageBox.Yes,
                QMessageBox.Yes
            )

            if rep == QMessageBox.Yes:
                win.quit()


        #-ini
        self.stng_lang_grp = QGroupBox(tr('Change Language'))
        self.stng_lang_grp.setMaximumSize(200, 130)
        # self.stng_lang_grp.setMinimumSize(500, 200)
        stng_lang_lay = QGridLayout()
        self.stng_lang_grp.setLayout(stng_lang_lay)

        tab_stng_lay.addWidget(self.stng_lang_grp, 1, 0)#, Qt.AlignRight)

        #-Langs combo box
        self.stng_lang_box = QComboBox()
        self.stng_lang_box.setMaximumWidth(50)
        self.stng_lang_box.addItems(langs_lst)
        self.stng_lang_box.setCurrentText(lang)
        stng_lang_lay.addWidget(self.stng_lang_box, 0, 0, Qt.AlignLeft)

        #-Button
        self.stng_lang_bt = QPushButton(tr('Apply'))
        stng_lang_lay.addWidget(self.stng_lang_bt, 1, 0, Qt.AlignRight)
        self.stng_lang_bt.clicked.connect(chg_lang)

        #---Button close
        self.close_bt = QPushButton(tr('Close'))
        self.close_bt.clicked.connect(self.close)
        tab_stng_lay.addWidget(self.close_bt, 2, 0, Qt.AlignRight)


    def use(style, app_style, parent=None):
        '''Function which launch this window.'''

        stg_win = SettingsWin(style, app_style, parent)
        stg_win.exec_()



##-run
if __name__ == '__main__':
    import sys

    if '-h' in sys.argv or '--help' in sys.argv:
        print('''Usage: {} [-h] [-v] [files ...]
Typt - type and encrypt

Options :
    -h, --help      Display help on commandline options and exit
    -v, --version   Display version information and exit
        '''.format(sys.argv[0]))

        sys.exit()

    elif '-v' in sys.argv or '--version' in sys.argv:
        print('Typt version\t\t: v{}\nTypt_gui.py version\t: v{}\nAES.py version\t\t: v{}'.format(Typt_version, Typt_gui__version, AES.version))
        sys.exit()

    else:
        files = sys.argv[1:]

        #------Launch the GUI
        TyptGui.use(files)

