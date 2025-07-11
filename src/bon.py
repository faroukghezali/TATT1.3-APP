import sqlite3
import sys
from decimal import Decimal

import openpyxl
from openpyxl.workbook import workbook
from PyQt6.QtCore import QDate, QStringListModel
from PyQt6.QtWidgets import (QApplication, QCompleter, QDateEdit, QFrame,
                             QHBoxLayout, QLineEdit, QListWidget, QMessageBox,
                             QPushButton, QSizePolicy, QSpinBox,
                             QStackedWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from database import get_rapport_dactivity
from wte import create_rapport
from wte import write_to_excel as wte


class CreatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_database()
        self.load_products()
        self.load_products()
        self.load_sku()
        self.load_matricule()
        self.load_tp()
        self.load_bon_list()
        self.conn = sqlite3.connect("main.db")
        self.c = self.conn.cursor()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        left_frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        left_frame.setLayout(layout)
        left_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # left_frame.setStyleSheet("background-color:green;")
        right_frame = QFrame()
        right_frame.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        # right_frame.setStyleSheet("background-color:blue;")
        list_layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.table_widget.cellChanged.connect(self.auto_save_on_cell_change)
        self.table_widget.setStyleSheet("background-color:white;color:black;")
        list_layout.addWidget(self.table_widget)
        right_frame.setLayout(list_layout)

        self.completer = QCompleter()
        self.sku_completer = QCompleter()
        self.matricule_completer = QCompleter()
        self.tp_completer = QCompleter()
        self.bon_completer = QCompleter()

        self.bon_number = QLineEdit(self)
        self.bon_number.setPlaceholderText("Numero de bon")
        self.bon_number.setMaximumWidth(200)
        self.bon_number.textChanged.connect(self.load_table_data)
        self.bon_number.setCompleter(self.bon_completer)

        self.bon_date = QDateEdit(self)
        self.bon_date.setCalendarPopup(True)
        self.bon_date.setDate(QDate.currentDate())
        self.bon_date.dateChanged.connect(self.on_date_change)
        self.bon_date.setMaximumWidth(200)

        self.matricule = QLineEdit(self)
        self.matricule.setPlaceholderText("Selectioné matricule")
        self.matricule.setCompleter(self.matricule_completer)
        self.matricule.textChanged.connect(self.on_matricule_change)

        self.tp = QLineEdit(self)
        self.tp.setPlaceholderText("Selectioné tp")
        self.tp.setCompleter(self.tp_completer)
        self.tp.textChanged.connect(self.on_tp_change)

        self.product_name = QLineEdit(self)
        self.product_name.setPlaceholderText("selectioné un article")
        self.product_name.setCompleter(self.completer)
        self.product_name.textChanged.connect(self.on_product_change)

        self.product_sku = QLineEdit(self)
        self.product_sku.setPlaceholderText("selectioné SKU")
        self.product_sku.setCompleter(self.sku_completer)
        self.product_sku.textChanged.connect(self.on_sku_change)

        self.product_quantity = QLineEdit(self)
        self.product_quantity.setPlaceholderText("Quantity")

        self.product_price = QLineEdit(self)
        self.product_price.setPlaceholderText("Prix")

        self.button_confirm = QPushButton("confirm", self)
        self.button_confirm.clicked.connect(self.bon_form_validate)

        self.button_excel = QPushButton("generate excel", self)
        self.button_excel.clicked.connect(self.generate_excel)

        self.button_rapport = QPushButton("Rapport", self)
        self.button_rapport.clicked.connect(self.get_rapport_dactivity_data)

        layout.addWidget(self.bon_number)
        layout.addWidget(self.bon_date)
        layout.addWidget(self.tp)
        layout.addWidget(self.matricule)
        layout.addWidget(self.product_sku)
        layout.addWidget(self.product_name)
        layout.addWidget(self.product_quantity)
        layout.addWidget(self.product_price)
        layout.addWidget(self.button_confirm)
        layout.addWidget(self.button_excel)
        layout.addWidget(self.button_rapport)
        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)

    def bon_form_validate(self):
        # Check if bon already exist else create it
        bon_number = self.bon_number.text()
        bon_date = self.bon_date.date().toString("dd/MM/yyyy")
        with sqlite3.connect("main.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id from  bon WHERE bon_number=?", (bon_number,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO bon(bon_number,bon_date) VALUES (?,?)",
                    (
                        bon_number,
                        bon_date,
                    ),
                )
                conn.commit()
        self.add_articles()

    def add_articles(self):
        # add Bon Items to the the article_bon table
        with sqlite3.connect("main.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id from bon WHERE bon_number=?", (self.bon_number.text(),)
            )
            bon_id = cursor.fetchone()
            product_price = Decimal(self.product_quantity.text()) * Decimal(
                self.product_price.text()
            )
            cursor.execute(
                "INSERT INTO article_bon(bus_id,product_name,product_quantity,product_price,bon_id) VALUES (?,?,?,?,?)",
                (
                    self.matricule.text(),
                    self.product_name.text(),
                    self.product_quantity.text(),
                    str(product_price),
                    bon_id[0],
                ),
            )
        # clear the form
        self.product_name.clear()
        self.product_price.clear()
        self.product_quantity.clear()
        self.load_table_data()
        wte(self.bon_number.text(), self.bon_date.text())

    def generate_excel(self, *args):
        return wte(self.bon_number.text(), self.bon_date.text())

    def get_rapport_dactivity_data(self, *args):
        return create_rapport(self.bon_number.text())

    def auto_save_on_cell_change(self, row, col):
        header = ("id", "product_name", "product_quantity", "product_price", "bus_id")
        value = self.table_widget.item(row, col).text()
        article_id = self.table_widget.item(row, 0).text()
        try:
            with sqlite3.connect("main.db") as conn:
                cursor = conn.cursor()
                if col != 0:
                    cursor.execute(
                        f"DELETE FROM article_bon  WHERE id = ?",
                        (
                            article_id,
                        ),
                    )
                    conn.commit()
                    self.load_table_data()
        except Exception as e:
            print(f"error happened : {e}")

    def load_table_data(self, *args):
        self.table_widget.clear()
        self.table_widget.blockSignals(True)
        # display the list value in the table
        header = ("id", "Produit", "quantity", "prix", "matricule")
        self.table_widget.setHorizontalHeaderLabels(header)

        with sqlite3.connect("main.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id ,product_name,product_quantity,product_price,bus_id FROM article_bon WHERE bon_id = (SELECT id FROM bon WHERE bon_number = ?)",
                (self.bon_number.text(),),
            )
            result = cursor.fetchall()

        if len(result) > 0:
            self.table_widget.setRowCount(len(result) + 10)
            self.table_widget.setColumnCount(len(result[0]))
        row_index = 0
        for value_tuple in result:
            col_index = 0
            for value in value_tuple:
                self.table_widget.setItem(
                    row_index, col_index, QTableWidgetItem(str(value))
                )
                col_index += 1
            row_index += 1
        self.table_widget.blockSignals(False)

    def write_to_excel(self):
        with sqlite3.connect("main.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT product_name,product_quantity,product_price,bus_id FROM article_bon WHERE bon_id = (SELECT id FROM bon WHERE bon_number = ?)",
                (self.bon_number.text(),),
            )
            result = cursor.fetchall()

        template = "template/bon.xlsx"
        workbook = openpyxl.load_workbook(template)
        sheet = workbook.active
        sheet["E6"] = f"BIS-N°{self.bon_number.text()}"
        sheet["E10"] = f"DATE : {self.bon_date.text()}"
        row_index = 15
        for value_tuple in result:
            col_index = 2
            for value in value_tuple:
                sheet.cell(row_index, col_index, value=str(value))
                col_index += 1
            row_index += 1

        workbook.save(f"template/{self.bon_number.text()}.xlsx")
        workbook.close()

        # Check if form isnot empty
        # write into excel

    def load_database(self):
        self.conn = sqlite3.connect("main.db")
        self.cursor = self.conn.cursor()

    def load_sku(self):
        self.cursor.execute("SELECT sku from  product")
        article = [row[0] for row in self.cursor.fetchall()]
        print(article)
        self.sku_completer.setModel(QStringListModel(article))

    def load_products(self):
        self.cursor.execute("SELECT name from  product")
        article = [row[0] for row in self.cursor.fetchall()]
        self.completer.setModel(QStringListModel(article))

    def load_matricule(self):
        print("INSIDE MATRICULE")
        self.cursor.execute("SELECT matricule from bus")
        matricule = [row[0] for row in self.cursor.fetchall()]
        self.matricule_completer.setModel(QStringListModel(matricule))

    def load_tp(self):
        self.cursor.execute("SELECT tp from bus")
        tp = [row[0] for row in self.cursor.fetchall()]
        self.tp_completer.setModel(QStringListModel(tp))

    def load_bon_list(self):
        print("bon list inside")
        self.cursor.execute("SELECT bon_number from bon")
        bon_number = [row[0] for row in self.cursor.fetchall()]
        print(f"BON NUMBERS {bon_number}")
        self.bon_completer.setModel(QStringListModel(bon_number))

    def on_sku_change(self, text):
        if text:
            self.cursor.execute(
                "SELECT quantity,price,name from product WHERE sku=?", (text,)
            )
            result = self.cursor.fetchone()
            if result:
                self.product_quantity.setText(str(result[0]))
                self.product_price.setText(str(result[1]))
                self.product_name.setText(str(result[2]))
            else:
                self.product_quantity.clear()
                self.product_price.clear()
                self.product_name.clear()

    def on_product_change(self, text):
        if text:
            self.cursor.execute(
                "SELECT quantity,price from product WHERE name=?", (text,)
            )
            result = self.cursor.fetchone()
            if result:
                self.product_quantity.setText(str(result[0]))
                self.product_price.setText(str(result[1]))
            else:
                self.product_quantity.clear()
                self.product_price.clear()

    def on_tp_change(self, text):
        if text:
            self.cursor.execute("SELECT tp,matricule from bus WHERE tp=?", (text,))
            result = self.cursor.fetchone()
            if result:
                self.tp.setText(result[0])
                self.matricule.setText(result[1])

    def on_matricule_change(self, text):
        print(text)
        if text:
            self.cursor.execute("SELECT matricule from bus WHERE matricule=?", (text,))
            result = self.cursor.fetchone()
            if result:
                self.matricule.setText(result[0])

    def on_date_change(self, date):
        print("WELCOM TO DATE CHANGE\n", date, "\n DATE IN STR", date.toString())


class BonCRUDApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Bus CRUD Application")
        self.layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget(self)
        self.create_page = CreatePage()
        self.stacked_widget.addWidget(self.create_page)
        self.layout.addWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.create_page)
        self.setLayout(self.layout)

    def show_create_page(self):
        self.stacked_widget.setCurrentWidget(self.create_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    style = app.style()
    print("Standard palette:", style.standardPalette().color(QPalette.Window).name())
    window = BonCRUDApp()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
