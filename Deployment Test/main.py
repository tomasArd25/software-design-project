import sys
import sqlite3
import bcrypt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui_main_page import Ui_MainWindow
from ui_login_page import Ui_LoginWindow
from ui_edit_page import Ui_EditWindow
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox, QWidget, QVBoxLayout

class Login_window(QMainWindow, Ui_LoginWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('Information System')
        self.showMaximized()
        self.create_login_db()

        self.login_function()

        self.hide_reg_wid()
        self.hide_all_login_warn()
        
        self.create_acc_btn.clicked.connect(self.hide_incorrect)
        self.login_btn.clicked.connect(self.hide_username_exists)
        
        self.sign_in_btn.clicked.connect(self.login_function)
        self.sign_up_btn.clicked.connect(self.signup_function)

        self.setAttribute(Qt.WA_DeleteOnClose)

    def hide_all_login_warn(self):
        self.hide_incorrect()
        self.hide_username_exists()
        self.hide_valid_username()
        self.hide_valid_password()
    
    def show_valid_username(self):
        self.username_valid_label.setVisible(True)

    def hide_valid_username(self):
        self.username_valid_label.setVisible(False)

    def show_valid_password(self):
        self.password_valid_label.setVisible(True)

    def hide_valid_password(self):
        self.password_valid_label.setVisible(False)

    def show_username_exists(self):
        self.username_exists_label.setVisible(True)

    def hide_username_exists(self):
        self.username_exists_label.setVisible(False)

    def show_incorrect(self):
        self.incorrect_label.setVisible(True)

    def hide_incorrect(self):
        self.incorrect_label.setVisible(False)

    def show_reg_wid(self):
        self.register_widget.setVisible(True)
        
    def hide_reg_wid(self):
        self.register_widget.setVisible(False)

    def show_login_wid(self):
        self.login_widget.setVisible(True)

    def hide_login_wid(self):
        self.login_widget.setVisible(False)

    def call_main_window(self):
        self.main_window = Main_window(self.access_username)
        self.main_window.show()
        self.hide()

    def create_login_db(self):
        conn = sqlite3.connect('login_accs.db')
        cursor = conn.cursor()
        query = f"""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                    )"""
        cursor.execute(query)
        cursor.close()
        conn.close()
    
    def signup_function(self):
        conn = sqlite3.connect('login_accs.db')
        cursor = conn.cursor()

        username = self.signup_username.text()
        password = self.signup_password.text()

        if username == '':
            self.show_valid_username()
            self.hide_valid_password()
            self.hide_username_exists()
        elif len(password)<8:
            self.hide_valid_username()
            self.show_valid_password()
            self.hide_username_exists()
        else:
            cursor.execute('SELECT username FROM users WHERE username=?', [username])
            if cursor.fetchone() is not None:
                self.hide_valid_username()
                self.hide_valid_password()
                self.show_username_exists()
            else:
                encoded_password = password.encode('utf-8')
                hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
                cursor.execute('INSERT INTO users VALUES (?, ?)',[username, hashed_password])
                conn.commit()
                msg = QMessageBox()
                msg.setWindowTitle('Success')
                msg.setText('Account created successfully.')
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(self.show_login_wid)
                msg.buttonClicked.connect(self.hide_reg_wid)
                msg.buttonClicked.connect(self.signup_username.clear)
                msg.buttonClicked.connect(self.signup_password.clear)
                msg.exec_()
                self.create_acc_btn.setChecked(True)
                self.hide_valid_username()
                self.hide_valid_password()
                self.hide_username_exists()
                cursor.close()
                conn.close()

    def login_function(self):
        conn = sqlite3.connect('login_accs.db')
        cursor = conn.cursor()

        username = self.login_username.text()
        password = self.login_password.text()

        self.access_username = username

        cursor.execute('SELECT password FROM users WHERE username=?', [username])
        result = cursor.fetchone()

        if result:
            if bcrypt.checkpw(password.encode('utf-8'), result[0]):
                msg = QMessageBox()
                msg.setWindowTitle('Success')
                msg.setText('Signed in successfully')
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(self.call_main_window)
                msg.exec_()
                cursor.close()
                conn.close()
            else:
                self.show_incorrect()
                cursor.close()
                conn.close()
        else:
            self.show_incorrect()
            cursor.close()
            conn.close()

class Main_window(QMainWindow, Ui_MainWindow):
    def __init__(self, username):
        super().__init__()
        self.setupUi(self)
        self.font_size_cb.setCurrentText("Medium")
        self.stackedWidget.setStyleSheet("QWidget{font-size:11pt;}")
        self.current_username = username
        self.setWindowTitle('SysInfo')
        self.showMaximized()
        self.create_database(self.current_username)
        self.load_data(f"SELECT * FROM '{self.current_username}'")
        self.username_label.setText(self.current_username)
        self.load_places()
        self.load_all_chart()
        
        self.result_table.verticalHeader().setVisible(False)
        self.icon_name_widget.setHidden(True)
        self.dashboard_name.setChecked(True)

        self.sorting_orders = [Qt.AscendingOrder] * self.result_table.columnCount()
        self.result_table.horizontalHeader().sectionClicked.connect(self.sort_table)

        self.non_editable()
        self.init_signal_slot()
        
    def resize_table(self):
        self.result_table.resizeRowsToContents()
        self.result_table.resizeColumnsToContents()
        
    def init_signal_slot(self):
        self.font_size_cb.currentIndexChanged.connect(self.set_font_size)

        self.dashboard_name.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.dashboard.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.dashboard_name.clicked.connect(self.load_all_chart)
        self.dashboard.clicked.connect(self.load_all_chart)

        self.table_name.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(1))
        self.table.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(1))

        self.settings_name.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(2))
        self.settings.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(2))

        self.signout_name.clicked.connect(self.signout_func)
        self.signout.clicked.connect(self.signout_func)

        self.region.currentIndexChanged.connect(self.load_province)
        self.province.currentIndexChanged.connect(self.load_city)
        self.city.currentIndexChanged.connect(self.load_brgy)
        
        self.show_btn.clicked.connect(lambda:self.load_data(f"SELECT * FROM '{self.current_username}'"))
        self.add_btn.clicked.connect(self.add_data)
        self.delete_btn.clicked.connect(self.delete_data)
        self.edit_btn.clicked.connect(self.edit_data)
        self.search_btn.clicked.connect(self.search_data)
        self.clear_sel_btn.clicked.connect(self.result_table.clearSelection)
        self.clear_data_btn.clicked.connect(self.clear_data)

    def sort_table(self, logical_index):
        current_order = self.sorting_orders[logical_index]
        if current_order == Qt.AscendingOrder:
            self.result_table.sortItems(logical_index, Qt.DescendingOrder)
            self.sorting_orders[logical_index] = Qt.DescendingOrder
        else:
            self.result_table.sortItems(logical_index, Qt.AscendingOrder)
            self.sorting_orders[logical_index] = Qt.AscendingOrder

    def cells_non_editable(self, row_count, col_count):
        for row in range(row_count):
            for col in range(col_count):
                item = self.result_table.item(row, col)
                if item is not None:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def non_editable(self):
        row_count = self.result_table.rowCount()
        col_count = self.result_table.columnCount()
        self.cells_non_editable(row_count, col_count)
    
    def signout_func(self):
        msg = QMessageBox()
        msg.setWindowTitle('Warning')
        msg.setText('Are you sure you want to sign out?')
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.buttonClicked.connect(self.call_login_window)
        msg.exec_()
    
    def call_login_window(self, button):
        if button.text() == "OK":
            self.login_window = Login_window()
            self.login_window.show()
            self.hide()

    def create_database(self, username):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        query = f""" CREATE TABLE IF NOT EXISTS "{username}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT DEFAULT NULL,
            last_name TEXT DEFAULT NULL,
            middle_name TEXT DEFAULT NULL,
            extension TEXT,
            birthdate TEXT,
            age INTEGER,
            sex TEXT,
            region TEXT,
            province TEXT,
            city TEXT,
            barangay TEXT,
            sitio TEXT,
            zip_code INTEGER DEFAULT NULL,
            citizenship TEXT,
            place_of_birth TEXT,
            civil_status TEXT,
            education TEXT,
            occupation TEXT)""" 
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()

    def load_data(self, query):
        try:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            self.result_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = NumericTableWidgetItem(value)
                    self.result_table.setItem(i, j, item)
            cursor.close()
            conn.close()
            self.resize_table()
        except Exception as e:
            return e
        self.non_editable()

    def add_data(self):
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            
            first_name = self.first_name.text().capitalize().strip()
            last_name = self.last_name.text().capitalize().strip()
            middle_name = self.middle_name.text().capitalize().strip()
            extension = self.extension.currentText()
            birthdate = self.birthdate.dateTime().toString('dd/MM/yyyy').strip()
            age = self.age.text().strip()
            sex = self.sex.currentText()
            region = self.region.currentText()
            province = self.province.currentText()
            city = self.city.currentText()
            barangay = self.barangay.currentText()
            sitio = self.sitio.currentText().capitalize().strip()
            zip_code = self.zip_code.text().strip()
            citizenship = self.citizenship.currentText()
            place_of_birth = self.place_of_birth.text().capitalize().strip()
            civil_status = self.civil_status.currentText()
            education = self.education.currentText()
            occupation = self.occupation.currentText()

            if not first_name or not last_name:
                msg = QMessageBox()
                msg.setWindowTitle('Enter data')
                msg.setText('First name and last name cannot be empty.')
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return

            cursor.execute(f"SELECT COUNT(*) FROM '{self.current_username}' WHERE first_name = ? AND last_name = ? AND birthdate = ?", 
                        (first_name, last_name, birthdate))
            if cursor.fetchone()[0] > 0:
                msg = QMessageBox()
                msg.setWindowTitle('Duplicate Entry')
                msg.setText('A record with the same first name, last name, and birthdate already exists.')
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return

            cursor.execute(f"""
                INSERT INTO "{self.current_username}" (first_name, last_name, middle_name, extension, 
                birthdate, age, sex, region, province, city, barangay, sitio, zip_code, citizenship, 
                place_of_birth, civil_status, education, occupation) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, (   
                first_name, last_name, middle_name, extension, 
                birthdate, age, sex, region, province, city, barangay, sitio, zip_code, citizenship, 
                place_of_birth, civil_status, education, occupation))
            
            conn.commit()
            self.load_data(f"SELECT * FROM '{self.current_username}'")
            self.non_editable()

        except sqlite3.Error as e:
            msg = QMessageBox()
            msg.setWindowTitle('Database Error')
            msg.setText(f"An error occurred: {e}")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def delete_data(self):
        selected_items = self.result_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            item_id = self.result_table.item(selected_row, 0).text()
            confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete the selected row?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.delete_from_database(item_id)
                self.result_table.removeRow(selected_row)
                self.reset_ids()
                self.load_data(f"SELECT * FROM '{self.current_username}'")
            
        else:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")

    def delete_from_database(self, item_id):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM '{self.current_username}' WHERE id=?", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def reset_ids(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM '{self.current_username}' ORDER BY id")
        rows = cursor.fetchall()

        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{self.current_username}'")
        for i, row in enumerate(rows):
            cursor.execute(f"UPDATE '{self.current_username}' SET id=? WHERE id=?", (i + 1, row[0]))
        
        conn.commit()
        cursor.close()
        conn.close()

    def edit_data(self):
        selected_items = self.result_table.selectedItems()

        if selected_items:

            self.edit_window = Edit_window()
            self.edit_window.show()

            selected_row = selected_items[0].row()

            first_name = self.result_table.item(selected_row, 1).text()
            last_name = self.result_table.item(selected_row, 2).text()
            middle_name = self.result_table.item(selected_row, 3).text()
            extension = self.result_table.item(selected_row, 4).text()

            birthdate_str = self.result_table.item(selected_row, 5).text()
            year, month, day = map(int, birthdate_str.split('/'))
            birthdate = QDate(day, month, year)

            age = self.result_table.item(selected_row, 6).text()
            sex = self.result_table.item(selected_row, 7).text()

            region = self.result_table.item(selected_row, 8).text()
            province = self.result_table.item(selected_row, 9).text()
            city = self.result_table.item(selected_row, 10).text()
            barangay = self.result_table.item(selected_row, 11).text()

            sitio = self.result_table.item(selected_row, 12).text()
            zip_code = self.result_table.item(selected_row, 13).text()
            citizenship = self.result_table.item(selected_row, 14).text()
            place_of_birth = self.result_table.item(selected_row, 15).text()
            civil_status = self.result_table.item(selected_row, 16).text()
            education = self.result_table.item(selected_row, 17).text()
            occupation = self.result_table.item(selected_row, 18).text()

            self.edit_window.first_name_edit.setText(first_name)
            self.edit_window.last_name_edit.setText(last_name)
            self.edit_window.middle_name_edit.setText(middle_name)
            self.edit_window.extension_edit.setCurrentText(extension)
            self.edit_window.birthdate_edit.setDate(birthdate)
            self.edit_window.age_edit.setValue(int(age))
            self.edit_window.sex_edit.setCurrentText(sex)

            self.edit_window.region_edit.setCurrentText(region)
            self.edit_window.province_edit.setCurrentText(province)
            self.edit_window.city_edit.setCurrentText(city)
            self.edit_window.barangay_edit.setCurrentText(barangay)

            self.edit_window.sitio_edit.setCurrentText(sitio)
            self.edit_window.zip_code_edit.setText(zip_code)
            self.edit_window.citizenship_edit.setCurrentText(citizenship)
            self.edit_window.place_of_birth_edit.setText(place_of_birth)
            self.edit_window.civil_status_edit.setCurrentText(civil_status)
            self.edit_window.education_edit.setCurrentText(education)
            self.edit_window.occupation_edit.setCurrentText(occupation)

            self.edit_window.save_btn_edit.clicked.connect(self.confirm_save)
            self.edit_window.discard_btn_edit.clicked.connect(self.confirm_discard)
                
        else:
            QMessageBox.warning(self, "No Selection", "Please select a row to edit.")
    
    def confirm_save(self):
        msg = QMessageBox()
        msg.setWindowTitle('Save')
        msg.setText('Do you want to save changes?')
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Cancel)
        response = msg.exec_()

        selected_items = self.result_table.selectedItems()
        selected_row = selected_items[0].row()
        item_id = self.result_table.item(selected_row, 0).text()
        
        first_name_edit = self.edit_window.first_name_edit.text().capitalize().strip()
        last_name_edit = self.edit_window.last_name_edit.text().capitalize().strip()
        middle_name_edit = self.edit_window.middle_name_edit.text().capitalize().strip()
        extension_edit = self.edit_window.extension_edit.currentText()
        birthdate_edit = self.edit_window.birthdate_edit.dateTime().toString('dd/MM/yyyy').strip()
        age_edit = self.edit_window.age_edit.text()
        sex_edit = self.edit_window.sex_edit.currentText()
        region_edit = self.edit_window.region_edit.currentText()
        province_edit = self.edit_window.province_edit.currentText()
        city_edit = self.edit_window.city_edit.currentText()
        barangay_edit = self.edit_window.barangay_edit.currentText()
        sitio_edit = self.edit_window.sitio_edit.currentText().capitalize().strip()
        zip_code_edit = self.edit_window.zip_code_edit.text()
        citizenship_edit = self.edit_window.citizenship_edit.currentText()
        place_of_birth_edit = self.edit_window.place_of_birth_edit.text().capitalize().strip()
        civil_status_edit = self.edit_window.civil_status_edit.currentText()
        education_edit = self.edit_window.education_edit.currentText()
        occupation_edit = self.edit_window.occupation_edit.currentText()

        if response == QMessageBox.Ok:
            self.result_table.setItem(selected_row, 1, QTableWidgetItem(first_name_edit))
            self.result_table.setItem(selected_row, 2, QTableWidgetItem(last_name_edit))
            self.result_table.setItem(selected_row, 3, QTableWidgetItem(middle_name_edit))
            self.result_table.setItem(selected_row, 4, QTableWidgetItem(extension_edit))
            self.result_table.setItem(selected_row, 5, QTableWidgetItem(birthdate_edit))
            self.result_table.setItem(selected_row, 6, QTableWidgetItem(age_edit))
            self.result_table.setItem(selected_row, 7, QTableWidgetItem(sex_edit))
            self.result_table.setItem(selected_row, 8, QTableWidgetItem(region_edit))
            self.result_table.setItem(selected_row, 9, QTableWidgetItem(province_edit))
            self.result_table.setItem(selected_row, 10, QTableWidgetItem(city_edit))
            self.result_table.setItem(selected_row, 11, QTableWidgetItem(barangay_edit))
            self.result_table.setItem(selected_row, 12, QTableWidgetItem(sitio_edit))
            self.result_table.setItem(selected_row, 13, QTableWidgetItem(zip_code_edit))
            self.result_table.setItem(selected_row, 14, QTableWidgetItem(citizenship_edit))
            self.result_table.setItem(selected_row, 15, QTableWidgetItem(place_of_birth_edit))
            self.result_table.setItem(selected_row, 16, QTableWidgetItem(civil_status_edit))
            self.result_table.setItem(selected_row, 17, QTableWidgetItem(education_edit))
            self.result_table.setItem(selected_row, 18, QTableWidgetItem(occupation_edit))

            self.update_row_in_db(item_id,
                first_name_edit, last_name_edit, middle_name_edit, extension_edit, birthdate_edit,
                age_edit, sex_edit, region_edit, province_edit, city_edit,
                barangay_edit, sitio_edit, zip_code_edit, citizenship_edit, place_of_birth_edit,
                civil_status_edit, education_edit, occupation_edit)

            msg = QMessageBox()
            msg.setWindowTitle('Success')
            msg.setText('Update success')
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self.resize_table()
            self.edit_window.close()
    
    def confirm_discard(self):
        msg = QMessageBox()
        msg.setWindowTitle('Discard')
        msg.setText('Do you want to discard changes?')
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Cancel)
        response = msg.exec_()
        if response == QMessageBox.Ok:
            self.edit_window.close()

    def update_row_in_db(self, item_id,
        first_name_edit, last_name_edit, middle_name_edit, extension_edit, birthdate_edit,
        age_edit, sex_edit, region_edit, province_edit, city_edit,
        barangay_edit, sitio_edit, zip_code_edit, citizenship_edit, place_of_birth_edit,
        civil_status_edit, education_edit, occupation_edit):

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"UPDATE '{self.current_username}' SET first_name=?, last_name=?, middle_name=?, extension=?, birthdate=?,age=?, sex=?, region=?, province=?, city=?,barangay=?, sitio=?, zip_code=?, citizenship=?, place_of_birth=?, civil_status=?, education=?, occupation=? WHERE id=?", (
        first_name_edit, last_name_edit, middle_name_edit, extension_edit, birthdate_edit,
        age_edit, sex_edit, region_edit, province_edit, city_edit,
        barangay_edit, sitio_edit, zip_code_edit, citizenship_edit, place_of_birth_edit,
        civil_status_edit, education_edit, occupation_edit, item_id))
        conn.commit()
        cursor.close()
        conn.close()

    def search_data(self):
        first_name = self.first_name.text().capitalize().strip()
        last_name = self.last_name.text().capitalize().strip()
        middle_name = self.middle_name.text().capitalize().strip()
        query = fr""" SELECT * FROM {self.current_username}
            WHERE first_name LIKE '{first_name}' AND
            last_name LIKE '{last_name}' AND
            middle_name LIKE '{middle_name}' """
        self.load_data(query)

    def clear_data(self):
        msg = QMessageBox()
        msg.setWindowTitle('Warning')
        msg.setText('Are you sure to clear all data? \n You cannot undo this action.')
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.buttonClicked.connect(self.clear_func)
        msg.exec_()
        self.load_data(f"SELECT * FROM '{self.current_username}'")
    
    def clear_func(self, button):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        if button.text() == 'OK':
            query = f"""DELETE FROM '{self.current_username}'"""
            cursor.execute(query)
            query = f"DELETE FROM sqlite_sequence WHERE name='{self.current_username}'"
            cursor.execute(query)
            conn.commit()
            cursor.close()
            conn.close()
            msg = QMessageBox()
            msg.setWindowTitle('Deleted')
            msg.setText('All data has been deleted')
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(lambda:self.table_name.setChecked(True))
            msg.buttonClicked.connect(lambda:self.stackedWidget.setCurrentIndex(1))
            msg.exec_()

    def load_places(self):
        self.load_region()
        self.set_initial_region('12')

        self.load_province()
        self.set_initial_province('1247')

        self.load_city()
        self.set_initial_city('124712')

        self.load_brgy()
        self.set_initial_brgy('124712025')

    def set_initial_region(self, region_data):
        for index in range(self.region.count()):
            item_data = self.region.itemData(index)
            if item_data == region_data:
                self.region.setCurrentIndex(index)
                return
            
    def set_initial_province(self, province_data):
        for index in range(self.province.count()):
            item_data = self.province.itemData(index)
            if item_data == province_data:
                self.province.setCurrentIndex(index)
                return

    def set_initial_city(self, city_data):
        for index in range(self.city.count()):
            item_data = self.city.itemData(index)
            if item_data == city_data:
                self.city.setCurrentIndex(index)
                return
            
    def set_initial_brgy(self, brgy_data):
        for index in range(self.barangay.count()):
            item_data = self.barangay.itemData(index)
            if item_data == brgy_data:
                self.barangay.setCurrentIndex(index)
                return
            
    def load_region(self):
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT regDesc, regCode FROM refregion")
        rows = cursor.fetchall()
        for row in rows:
            self.region.addItem(row[0])
            self.region.setItemData(self.region.count() - 1, row[1])
        cursor.close()
        conn.close()

    def load_province(self):
        self.province.clear()
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        region_current_index = self.region.currentIndex()
        region_item_data = self.region.itemData(region_current_index)
        cursor.execute("SELECT provDesc, provCode FROM refprovince WHERE regCode=?",(region_item_data,))
        rows = cursor.fetchall()
        for row in rows:
            self.province.addItem(row[0])
            self.province.setItemData(self.province.count() - 1, row[1])
        self.load_city()
        cursor.close()
        conn.close()
    
    def load_city(self):
        self.city.clear()
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        province_current_index = self.province.currentIndex()
        province_item_data = self.province.itemData(province_current_index)
        cursor.execute("SELECT citymunDesc, citymunCode FROM refcitymun WHERE provCode=?",(province_item_data,))
        rows = cursor.fetchall()
        for row in rows:
            self.city.addItem(row[0])
            self.city.setItemData(self.city.count() - 1, row[1])
        self.load_brgy()
        cursor.close()
        conn.close()
    
    def load_brgy(self):
        self.barangay.clear()
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        city_current_index = self.city.currentIndex()
        city_item_data = self.city.itemData(city_current_index)
        cursor.execute("SELECT brgyDesc, brgyCode FROM refbrgy WHERE citymunCode=?",(city_item_data,))
        rows = cursor.fetchall()
        for row in rows:
            self.barangay.addItem(row[0])
            self.barangay.setItemData(self.barangay.count() - 1, row[1])
        cursor.close()
        conn.close()

    def load_all_chart(self):
        self.load_population_chart()
        self.load_age_chart()
        self.load_sex_chart()
        self.load_civil_status_chart()
        self.load_edu_chart()
        self.load_occupation_chart()

    def load_population_chart(self):
        if self.population_widget.layout() is not None:
            QWidget().setLayout(self.population_widget.layout())
        self.central_widget = self.population_widget
        self.layout = QVBoxLayout(self.central_widget)
        self.matplotlib_widget = MatplotlibWidget(self.current_username)
        self.layout.addWidget(self.matplotlib_widget)
        self.matplotlib_widget.current_population()

    def load_age_chart(self):
        if self.age_widget.layout() is not None:
            QWidget().setLayout(self.age_widget.layout())
        self.central_widget = self.age_widget
        self.layout = QVBoxLayout(self.central_widget)
        self.matplotlib_widget = MatplotlibWidget(self.current_username)
        self.layout.addWidget(self.matplotlib_widget)
        self.matplotlib_widget.age_chart()

    def load_sex_chart(self):
        if self.sex_widget.layout() is not None:
            QWidget().setLayout(self.sex_widget.layout())
        self.central_widget = self.sex_widget
        self.layout = QVBoxLayout(self.central_widget)
        self.matplotlib_widget = MatplotlibWidget(self.current_username)
        self.layout.addWidget(self.matplotlib_widget)
        self.matplotlib_widget.sex_chart()
    
    def load_civil_status_chart(self):
        if self.civil_status_widget.layout() is not None:
            QWidget().setLayout(self.civil_status_widget.layout())
        self.central_widget = self.civil_status_widget
        self.layout = QVBoxLayout(self.central_widget)
        self.matplotlib_widget = MatplotlibWidget(self.current_username)
        self.layout.addWidget(self.matplotlib_widget)
        self.matplotlib_widget.civil_status_chart()

    def load_edu_chart(self):
        if self.edu_widget.layout() is not None:
            QWidget().setLayout(self.edu_widget.layout())
        self.central_widget = self.edu_widget
        self.layout = QVBoxLayout(self.central_widget)
        self.matplotlib_widget = MatplotlibWidget(self.current_username)
        self.layout.addWidget(self.matplotlib_widget)
        self.matplotlib_widget.edu_chart()

    def load_occupation_chart(self):
        if self.occupation_widget.layout() is not None:
            QWidget().setLayout(self.occupation_widget.layout())
        self.central_widget = self.occupation_widget
        self.layout = QVBoxLayout(self.central_widget)
        self.matplotlib_widget = MatplotlibWidget(self.current_username)
        self.layout.addWidget(self.matplotlib_widget)
        self.matplotlib_widget.occupation_chart()
    
    def set_font_size(self):
        font_size = self.font_size_cb.currentText()
        if font_size == "Small":
            self.stackedWidget.setStyleSheet("QWidget{font-size:9pt;}")
        elif font_size == "Medium":
            self.stackedWidget.setStyleSheet("QWidget{font-size:12pt;}")
        elif font_size == "Large":
            self.stackedWidget.setStyleSheet("QWidget{font-size:15pt;}")
    
class MatplotlibWidget(QWidget):
    def __init__(self, current_username):
        self.current_username = current_username
        super(MatplotlibWidget, self).__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def current_population(self):
        conn = sqlite3.connect('data.db')
        try:
            query = f"SELECT COUNT(*) FROM '{self.current_username}'"
            total_population = pd.read_sql_query(query, conn).iloc[0, 0]
        except Exception as e:
            print(f"Error: {e}")
            return
        finally:
            conn.close()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('#111111')
        ax.set_facecolor('#111111')
        ax.text(0.5, 0.5, f"Total recorded population: {total_population}", color='white', fontsize=12, ha='center', va='center')
        ax.axis('off')
        self.canvas.draw()

    def age_chart(self):
        conn = sqlite3.connect('data.db')
        try:
            bins = [0, 18, 30, 40, 50, 60, 70, 120]
            labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71+']
            query = f"SELECT age FROM '{self.current_username}'"
            df = pd.read_sql_query(query, conn)
            age_ranges = pd.cut(df['age'], bins=bins, labels=labels, right=False)
        except Exception as e:
            print(f"Error: {e}")
            return
        finally:
            conn.close()
        if df.empty:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No recorded data', horizontalalignment='center', verticalalignment='center', fontsize=12, color='white', bbox=dict(facecolor='#111111', edgecolor='none'))
            ax.axis('off')
            self.canvas.draw()
            return
        category_counts = age_ranges.value_counts().sort_index()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('#111111')
        ax.set_facecolor('#111111')
        legend_labels = [f'{label}: {count}' for label, count in zip(labels, category_counts)]
        wedges, texts, autotexts = ax.pie(category_counts, autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
        ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title('Age Distribution', color='white')
        self.canvas.draw()

    def sex_chart(self):
        conn = sqlite3.connect('data.db')
        try:
            query = f"SELECT sex FROM '{self.current_username}'"
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error: {e}")
            return
        finally:
            conn.close()
        if df.empty:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No recorded data', horizontalalignment='center', verticalalignment='center', fontsize=12, color='white', bbox=dict(facecolor='#111111', edgecolor='none'))
            ax.axis('off')
            self.canvas.draw()
            return
        category_counts = df['sex'].value_counts().sort_index()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('#111111')
        ax.set_facecolor('#111111')
        legend_labels = [f'{label}: {count}' for label, count in zip(category_counts.index, category_counts)]
        wedges, texts, autotexts = ax.pie(category_counts, autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
        ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title('Sex Distribution', color='white')
        self.canvas.draw()

    def civil_status_chart(self):
        conn = sqlite3.connect('data.db')
        try:
            query = f"SELECT civil_status FROM '{self.current_username}'"
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error: {e}")
            return
        finally:
            conn.close()
        if df.empty:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No recorded data', horizontalalignment='center', verticalalignment='center', fontsize=12, color='white', bbox=dict(facecolor='#111111', edgecolor='none'))
            ax.axis('off')
            self.canvas.draw()
            return
        category_counts = df['civil_status'].value_counts().sort_index()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('#111111')
        ax.set_facecolor('#111111')
        legend_labels = [f'{label}: {count}' for label, count in zip(category_counts.index, category_counts)]
        wedges, texts, autotexts = ax.pie(category_counts, autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
        ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title('Civil Status Distribution', color='white')
        self.canvas.draw()

    def edu_chart(self):
        conn = sqlite3.connect('data.db')
        try:
            query = f"SELECT education FROM '{self.current_username}'"
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error: {e}")
            return
        finally:
            conn.close()
        if df.empty:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No recorded data', horizontalalignment='center', verticalalignment='center', fontsize=12, color='white', bbox=dict(facecolor='#111111', edgecolor='none'))
            ax.axis('off')
            self.canvas.draw()
            return
        category_counts = df['education'].value_counts().sort_index()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('#111111')
        ax.set_facecolor('#111111')
        legend_labels = [f'{label}: {count}' for label, count in zip(category_counts.index, category_counts)]
        wedges, texts, autotexts = ax.pie(category_counts, autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
        ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title('Education Level Distribution', color='white')
        box = ax.get_position()
        ax.set_position([box.x0 - 0.2, box.y0, box.width, box.height])
        self.canvas.draw()

    def occupation_chart(self):
        conn = sqlite3.connect('data.db')
        try:
            query = f"SELECT occupation FROM '{self.current_username}'"
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error: {e}")
            return
        finally:
            conn.close()
        if df.empty:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No recorded data', horizontalalignment='center', verticalalignment='center', fontsize=12, color='white', bbox=dict(facecolor='#111111', edgecolor='none'))
            ax.axis('off')
            self.canvas.draw()
            return
        category_counts = df['occupation'].value_counts().sort_index()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('#111111')
        ax.set_facecolor('#111111')
        legend_labels = [f'{label}: {count}' for label, count in zip(category_counts.index, category_counts)]
        wedges, texts, autotexts = ax.pie(category_counts, autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
        ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title('Occupation Distribution', color='white')
        box = ax.get_position()
        ax.set_position([box.x0 - 0.25, box.y0, box.width, box.height])
        self.canvas.draw()

class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, value):
        super().__init__(str(value))

    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return super().__lt__(other)

class Edit_window(QWidget, Ui_EditWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowTitle('Edit')

        self.region_edit.currentIndexChanged.connect(self.load_province_edit)
        self.province_edit.currentIndexChanged.connect(self.load_city_edit)
        self.city_edit.currentIndexChanged.connect(self.load_brgy_edit)

        self.load_places_edit()

    def load_places_edit(self):
        self.load_region_edit()
        self.load_province_edit()
        self.load_city_edit()
        self.load_brgy_edit()

    def load_region_edit(self):
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT regDesc, regCode FROM refregion")
        rows = cursor.fetchall()
        for row in rows:
            self.region_edit.addItem(row[0])
            self.region_edit.setItemData(self.region_edit.count() - 1, row[1])
        cursor.close()
        conn.close()

    def load_province_edit(self):
        self.province_edit.clear()
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        region_current_index = self.region_edit.currentIndex()
        region_item_data = self.region_edit.itemData(region_current_index)
        cursor.execute("SELECT provDesc, provCode FROM refprovince WHERE regCode=?",(region_item_data,))
        rows = cursor.fetchall()
        for row in rows:
            self.province_edit.addItem(row[0])
            self.province_edit.setItemData(self.province_edit.count() - 1, row[1])
        self.load_city_edit()
        cursor.close()
        conn.close()
    
    def load_city_edit(self):
        self.city_edit.clear()
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        province_current_index = self.province_edit.currentIndex()
        province_item_data = self.province_edit.itemData(province_current_index)
        cursor.execute("SELECT citymunDesc, citymunCode FROM refcitymun WHERE provCode=?",(province_item_data,))
        rows = cursor.fetchall()
        for row in rows:
            self.city_edit.addItem(row[0])
            self.city_edit.setItemData(self.city_edit.count() - 1, row[1])
        cursor.close()
        conn.close()
    
    def load_brgy_edit(self):
        self.barangay_edit.clear()
        conn = sqlite3.connect('places_data.db')
        cursor = conn.cursor()
        city_current_index = self.city_edit.currentIndex()
        city_item_data = self.city_edit.itemData(city_current_index)
        cursor.execute("SELECT brgyDesc, brgyCode FROM refbrgy WHERE citymunCode=?",(city_item_data,))
        rows = cursor.fetchall()
        for row in rows:
            self.barangay_edit.addItem(row[0])
            self.barangay_edit.setItemData(self.barangay_edit.count() - 1, row[1])
        print
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Login_window()
    # w = Main_window('user')
    w.show()
    app.exec()
