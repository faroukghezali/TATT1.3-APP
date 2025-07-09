import sqlite3
import sys

from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bon import BonCRUDApp
from database import create_database
from main import BusCRUDApp
from product import ProductCRUDApp


class HomePage(QWidget):
    pass


class BusPage(QWidget):
    pass


class BonPage(QWidget):
    pass


class RapportPage(QWidget):
    pass


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        create_database()
        self.initUi()

    def initUi(self):
        self.setStyleSheet("background-color:#2F2F2F;")
        self.setWindowTitle("TATT BON ET RAPPORT")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 5, 30, 50)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # home_button = QPushButton("Home")
        # home_button.clicked.connect(self.open_home)
        bus_button = QPushButton("Bus")
        bus_button.clicked.connect(self.open_bus_app)
        product_button = QPushButton("Article")
        product_button.clicked.connect(self.open_product_app)
        bon_button = QPushButton("Bon")
        bon_button.clicked.connect(self.open_bon_page)
        rapport_button = QPushButton("Rapport")

        navigation = QHBoxLayout()
        navigation.setSpacing(5)

        # navigation.addWidget(home_button)
        navigation.addWidget(bus_button)
        navigation.addWidget(product_button)
        navigation.addWidget(bon_button)
        # navigation.addWidget(rapport_button)
        navigation.addStretch()
        main_layout.addLayout(navigation)

        self.stacked_widget = QStackedWidget(self)
        # self.home_page = HomePage()
        self.bon_page = BonCRUDApp()
        self.bus_page = BusCRUDApp()
        self.product_page = ProductCRUDApp()
        self.rapport_page = RapportPage()

        # self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.bus_page)
        self.stacked_widget.addWidget(self.bon_page)
        # self.stacked_widget.addWidget(self.rapport_page)
        self.stacked_widget.addWidget(self.bus_page)
        self.stacked_widget.addWidget(self.product_page)
        main_layout.addWidget(self.stacked_widget)

    def open_bus_app(self):
        self.stacked_widget.setCurrentWidget(self.bus_page)

    def open_bon_page(self):
        self.stacked_widget.setCurrentWidget(self.bon_page)

    def open_product_app(self):
        self.stacked_widget.setCurrentWidget(self.product_page)

    def open_home(self):
        self.stacked_widget.setCurrentWidget(self.home_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
