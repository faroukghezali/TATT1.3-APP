import sqlite3
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
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


palette = QPalette()
# Set individual colors
palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))  # Dark background
palette.setColor(
    QPalette.ColorRole.WindowText, QColor(Qt.GlobalColor.white)
)  # White text
palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))  # Dark buttons
palette.setColor(
    QPalette.ColorRole.ButtonText, QColor(Qt.GlobalColor.white)
)  # White button text
palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))  # Purple highlight
palette.setColor(
    QPalette.ColorRole.HighlightedText, QColor(Qt.GlobalColor.black)
)  # Black highlighted text
palette.setColor(
    QPalette.ColorRole.PlaceholderText, QColor(150, 150, 150)
)  # Light gray placeholder

palette.setColor(
    QPalette.ColorRole.AlternateBase, QColor(66, 66, 66)
)  # Darker alternate background
palette.setColor(
    QPalette.ColorRole.Base, QColor(53, 53, 53)
)  # Base color for text input
palette.setColor(QPalette.ColorRole.Text, QColor(Qt.GlobalColor.white))  # Text color
palette.setColor(
    QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220)
)  # Tooltip background
palette.setColor(
    QPalette.ColorRole.ToolTipText, QColor(Qt.GlobalColor.black)
)  # Tooltip text color
palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))  # Link color
palette.setColor(
    QPalette.ColorRole.LinkVisited, QColor(85, 26, 139)
)  # Visited link color
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setPalette(palette)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
