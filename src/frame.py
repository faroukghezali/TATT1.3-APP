import sqlite3
import sys

from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCompleter,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class BusApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.create_database()
        self.load_matricules()

    def initUI(self):
        self.setWindowTitle("Bus Registration")

        self.layout = QVBoxLayout()

        self.matricule_edit = QLineEdit(self)
        self.matricule_edit.setPlaceholderText("Enter Matricule")
        self.layout.addWidget(self.matricule_edit)

        self.brand_edit = QLineEdit(self)
        self.brand_edit.setPlaceholderText("Brand (Auto-filled)")
        self.brand_edit.setReadOnly(True)  # Make it read-only
        self.layout.addWidget(self.brand_edit)

        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.clicked.connect(self.on_confirm)
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)

        # Set up completer for matricule
        self.completer = QCompleter(self)
        self.matricule_edit.setCompleter(self.completer)
        self.matricule_edit.textChanged.connect(self.on_matricule_changed)

    def create_database(self):
        self.conn = sqlite3.connect("bus.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT NOT NULL UNIQUE,
                brand TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def load_matricules(self):
        self.cursor.execute("SELECT matricule FROM bus")
        print(f" cursor : {self.cursor.fetchall()} \n")
        matricules = [row[0] for row in self.cursor.fetchall()]
        print(f"matricules : {matricules} \n")
        self.completer.setModel(QStringListModel(matricules))

    def on_matricule_changed(self, text):
        if text:
            self.cursor.execute("SELECT brand FROM bus WHERE matricule = ?", (text,))
            result = self.cursor.fetchone()
            if result:
                self.brand_edit.setText(result[0])
            else:
                self.brand_edit.clear()

    def on_confirm(self):
        matricule = self.matricule_edit.text()
        brand = self.brand_edit.text()
        if matricule and brand:
            print(f"Matricule: {matricule}, Brand: {brand}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in both fields.")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    bus_app = BusApp()
    bus_app.show()
    sys.exit(app.exec())
