import sqlite3
import sys
from random import random
import csv
from shutil import copy2

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QMessageBox

#функция получения словаря жанров
def get_genres(cur) -> map:
    receive = cur.execute("SELECT * FROM genres").fetchall() #запрашиваем полную таблицу
    res = {} #возвращаемый словарь
    for row in enumerate(receive): #из каждой строки
        res[row[1][0]] = str(row[1][1]) #собираем словарь
    return res

#класс главного окна
class MyWidget(QMainWindow):
    #конструктор
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/task11.ui", self)
        
		#назначаем обработчик для кнопок
        self.pB_AddFilm.clicked.connect(self.add_film) #назначаем обработчик кнопки
        self.pB_EditFilm.clicked.connect(self.edit_film) #назначаем обработчик кнопки
        self.pB_DelFilm.clicked.connect(self.del_film) #назначаем обработчик кнопки
        self.pB_AddGenre.clicked.connect(self.add_genre) #назначаем обработчик кнопки
        self.pB_EditGenre.clicked.connect(self.edit_genre) #назначаем обработчик кнопки
        self.pB_DelGenre.clicked.connect(self.del_genre) #назначаем обработчик кнопки
        self.tabWidget.currentChanged.connect(self.tab_changed)

        copy2("res/films_db.sqlite", "res/films_db_tmp.sqlite") #копируем БД в буфер
        self.con = sqlite3.connect("res/films_db_tmp.sqlite") #присоединяем БД
        self.genres = None

        self.load_tW_Films() #загружаем таблицу
        self.load_tW_Genres() #загружаем таблицу

    #обработчик для смены вкладки
    def tab_changed(self, index: int):
        if (index == 0):
            self.load_tW_Films()
        pass

    def load_tW_Films(self):
        cur = self.con.cursor()
        self.genres = get_genres(cur) #получаем словарь жанров
        result = cur.execute(f"SELECT * FROM films").fetchall() #получили полную таблицу
        #заполнили размеры таблицы
        self.tW_Films.setRowCount(len(result))
        self.tW_Films.setColumnCount(len(result[0]))
        #заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                try:
                    tmp = self.genres[val] if j == 3 else val #для жанра получаем по ключу
                    self.tW_Films.setItem(i, j, QTableWidgetItem(str(tmp)))
                except:
                    self.tW_Films.setItem(i, j, QTableWidgetItem(str("error")))
        cur.close()

    def load_tW_Genres(self):
        cur = self.con.cursor()
        result = cur.execute(f"SELECT * FROM genres").fetchall() #получили полную таблицу
        #заполнили размеры таблицы
        self.tW_Genres.setRowCount(len(result))
        self.tW_Genres.setColumnCount(len(result[0]))
        #заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tW_Genres.setItem(i, j, QTableWidgetItem(str(val)))
        cur.close()

    #метод добавления записи
    def add_film(self):
        cur = self.con.cursor() #получаем курсор
        self.dialog = MyDialog() #объявляем диалоговое окно

        self.dialog.exec() #запускаем его
        if self.dialog.result() == 0: return #если произошла отмена - выходим
        
        #заполняем данные из диалога
        nomer = cur.execute(f"SELECT max(id) FROM films").fetchone()[0] #ИД с автоинкрементом
        name = self.dialog.Data[0]
        year = self.dialog.Data[1]
        genre = list(self.genres.keys())[list(self.genres.values()).index(self.dialog.Data[2])] #самый простой способ получить ключ по значению (почему нет такого метода у словаря?)
        length = self.dialog.Data[3]
        
        cur.execute(f"INSERT INTO films VALUES ({nomer+1},'{name}',{year},{genre},{length})") #делаем вставку
        self.statusBar().showMessage(f"Запись была добавлена") #уведомляем
        self.load_tW_Films() #снова загружаем таблицу
        cur.close()
        pass

    #метод добавления записи
    def edit_film(self):
        if len(self.tW_Films.selectedIndexes()) == 0:
            self.statusBar().showMessage(f"Выберите строку для изменения") #уведомляем
            return

        data = []
        for i in range(4):
            data.append(self.tW_Films.selectedIndexes()[i+1].data())
        cur = self.con.cursor() #получаем курсор
        self.dialog = MyDialog(True,data) #объявляем диалоговое окно

        self.dialog.exec() #запускаем его
        if self.dialog.result() == 0: return #если произошла отмена - выходим
        
        #заполняем данные из диалога
        nomer = self.tW_Films.selectedIndexes()[0].data() #ИД с автоинкрементом
        name = self.dialog.Data[0]
        year = self.dialog.Data[1]
        genre = list(self.genres.keys())[list(self.genres.values()).index(self.dialog.Data[2])] #самый простой способ получить ключ по значению (почему нет такого метода у словаря?)
        length = self.dialog.Data[3]
        
        cur.execute(f"""UPDATE films SET title='{name}', year={year}, genre={genre}, duration={length}
                            WHERE id = {nomer}""") #делаем вставку
        self.statusBar().showMessage(f"Запись была изменена") #уведомляем
        self.load_tW_Films() #снова загружаем таблицу
        cur.close()
        pass

    def del_film(self):
        if len(self.tW_Films.selectedIndexes()) == 0:
            self.statusBar().showMessage(f"Выберите строку для удаления") #уведомляем
            return

        id_f = int(self.tW_Films.selectedIndexes()[0].data())
        cur = self.con.cursor() #получаем курсор

        ok = QMessageBox.question(self,'Удаление', f'Действительно удалить фильм с id = {id_f}', QMessageBox.Yes, QMessageBox.No)

        if ok == QMessageBox.Yes:
            cur.execute(f"DELETE FROM films WHERE id = {id_f}")
            self.statusBar().showMessage(f"Запись была удалена") #уведомляем
            self.load_tW_Films() #снова загружаем таблицу
        cur.close()
        pass

    def add_genre(self):
        cur = self.con.cursor() #получаем курсор
        inp = QInputDialog().getText(self,'Добавление жанра','Название')

        if inp[1] == 0: return #если произошла отмена - выходим
        
        #заполняем данные из диалога
        nomer = cur.execute(f"SELECT max(id) FROM genres").fetchone()[0] #ИД с автоинкрементом
        name = inp[0]
        
        cur.execute(f"INSERT INTO genres VALUES ({nomer+1},'{name}')") #делаем вставку
        
        self.statusBar().showMessage(f"Запись была добавлена") #уведомляем
        self.load_tW_Genres() #снова загружаем таблицу
        cur.close()
        pass

    def edit_genre(self):
        if len(self.tW_Genres.selectedIndexes()) == 0:
            self.statusBar().showMessage(f"Выберите строку для изменения") #уведомляем
            return

        cur = self.con.cursor() #получаем курсор
        inp = QInputDialog().getText(self,'Изменение жанра','Название', text = self.tW_Genres.selectedIndexes()[1].data()) #объявляем диалоговое окно

        if inp[1] == 0: return #если произошла отмена - выходим
        
        #заполняем данные из диалога
        nomer = self.tW_Genres.selectedIndexes()[0].data() #ИД с автоинкрементом
        name = inp[0]
        
        cur.execute(f"""UPDATE genres SET title='{name}' WHERE id = {nomer}""") #делаем вставку
        self.statusBar().showMessage(f"Запись была изменена") #уведомляем
        self.load_tW_Genres() #снова загружаем таблицу
        cur.close()
        pass

    def del_genre(self):
        if len(self.tW_Genres.selectedIndexes()) == 0:
            self.statusBar().showMessage(f"Выберите строку для удаления") #уведомляем
            return

        id_f = int(self.tW_Genres.selectedIndexes()[0].data())
        cur = self.con.cursor() #получаем курсор

        ok = QMessageBox.question(self,'Удаление', f'Действительно удалить жанр с id = {id_f}', QMessageBox.Yes, QMessageBox.No)

        if ok == QMessageBox.Yes:
            cur.execute(f"DELETE FROM genres WHERE id = {id_f}")
            self.statusBar().showMessage(f"Запись была удалена") #уведомляем
            self.load_tW_Genres() #снова загружаем таблицу
        cur.close()
        pass

#класс диалога
class MyDialog(QDialog):
    def __init__(self, isEdit = False, data = []):
        super().__init__()
        uic.loadUi("ui/dialog_add.ui", self)
        
        self.setModal(True) #указываем, что диалог модальный
        self.pB_Accept.clicked.connect(self.pB_Click) #назначаем обработчик кнопки
        self.cB_Genre.addItems(list(get_genres().values())) #заполняем комбобокс жанрами
        self.Data = [] #массив данных

        if isEdit:
            self.lE_Name.setText(data[0])
            self.sB_Year.setValue(int(data[1]))
            self.cB_Genre.setCurrentText(data[2])
            self.sB_Length.setValue(int(data[3]))

    #обработчки кнопки Принять
    def pB_Click(self):
        if self.lE_Name.text() == "": #если название пустое
            self.label_Status.setText("Заполните Название") #уведомляем и выходим
            return
        #добавляем данные
        self.Data.append(self.lE_Name.text()) 
        self.Data.append(self.sB_Year.value())
        self.Data.append(self.cB_Genre.currentText())
        self.Data.append(self.sB_Length.value())
        self.accept() #диалог успешно закрывается 
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
