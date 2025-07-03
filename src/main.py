import sqlite3
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class CreatePage(QWidget):
    def __init__(self, load_buses_callback):
        super().__init__()
        self.load_buses_callback = load_buses_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.matricule_input = QLineEdit(self)
        self.matricule_input.setPlaceholderText("Matricule (Unique)")

        self.tp_input = QLineEdit(self)
        self.tp_input.setPlaceholderText("TP (unique)")

        self.brand_input = QLineEdit(self)
        self.brand_input.setPlaceholderText("Brand")

        self.add_button = QPushButton("Add Bus", self)
        self.add_button.clicked.connect(self.add_bus)

        layout.addWidget(self.matricule_input)
        layout.addWidget(self.tp_input)
        layout.addWidget(self.brand_input)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def add_bus(self):
        matricule = self.matricule_input.text()
        tp = self.tp_input.text()
        brand = self.brand_input.text()

        if matricule and brand:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO bus (matricule,tp, brand) VALUES (?,?,?)",
                    (matricule, tp, brand),
                )
                conn.commit()
                QMessageBox.information(self, "Success", "Bus added successfully.")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Input Error", "Matricule must be unique.")
            conn.close()
            self.load_buses_callback()
            self.matricule_input.clear()
            self.tp_input.clear()
            self.brand_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")


class ListPage(QWidget):
    def __init__(self, load_buses_callback, switch_to_update_callback):
        super().__init__()
        self.load_buses_callback = load_buses_callback
        self.switch_to_update_callback = switch_to_update_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.bus_list = QListWidget(self)
        self.bus_list.itemClicked.connect(self.load_selected_bus)
        layout.addWidget(self.bus_list)

        self.delete_button = QPushButton("Delete Bus", self)
        self.delete_button.clicked.connect(self.delete_bus)
        layout.addWidget(self.delete_button)

        self.update_button = QPushButton("Update Bus", self)
        self.update_button.clicked.connect(self.switch_to_update)
        layout.addWidget(self.update_button)

        self.setLayout(layout)
        self.load_buses()

    def load_buses(self):
        self.bus_list.clear()
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bus")
        buses = cursor.fetchall()
        for bus in buses:
            self.bus_list.addItem(
                f"{bus[1]} - {bus[2]} - {bus[3]}"
            )  # Display matricule and brand
        conn.close()

    def load_selected_bus(self, item):
        self.selected_matricule = item.text().split(" - ")[0]

    def delete_bus(self):
        if hasattr(self, "selected_matricule"):
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM bus WHERE matricule=?", (self.selected_matricule,)
            )
            conn.commit()
            conn.close()
            self.load_buses()
            QMessageBox.information(self, "Success", "Bus deleted successfully.")
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a bus to delete."
            )

    def switch_to_update(self):
        if hasattr(self, "selected_matricule"):
            self.switch_to_update_callback(self.selected_matricule)
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a bus to update."
            )


class UpdatePage(QWidget):
    def __init__(self, load_buses_callback):
        super().__init__()
        self.load_buses_callback = load_buses_callback
        self.initUI()
        self.selected_matricule = None

    def initUI(self):
        layout = QVBoxLayout()

        self.matricule_input = QLineEdit(self)
        self.matricule_input.setPlaceholderText("Matricule (Unique)")
        self.matricule_input.setReadOnly(True)  # Matricule should not be editable
        layout.addWidget(self.matricule_input)

        self.tp_input = QLineEdit(self)
        self.tp_input.setPlaceholderText("TP (UNIQUE)")
        layout.addWidget(self.tp_input)

        self.brand_input = QLineEdit(self)
        self.brand_input.setPlaceholderText("Brand")
        layout.addWidget(self.brand_input)

        self.update_button = QPushButton("Update Bus", self)
        self.update_button.clicked.connect(self.update_bus)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def load_bus(self, matricule):
        self.selected_matricule = matricule
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bus WHERE matricule=?", (matricule,))
        bus = cursor.fetchone()
        conn.close()

        if bus:
            self.matricule_input.setText(bus[1])  # Set matricule
            self.brand_input.setText(bus[2])  # Set brand
            self.tp_input.setText(bus[3])

    def update_bus(self):
        if self.selected_matricule:
            brand = self.brand_input.text()
            tp = self.tp_input.text()

            if brand:
                conn = sqlite3.connect("main.db")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE bus SET brand=?,tp=? WHERE matricule=?",
                    (brand, tp, self.selected_matricule),
                )
                conn.commit()
                conn.close()
                self.load_buses_callback()
                QMessageBox.information(self, "Success", "Bus updated successfully.")
                self.clear_inputs()
            else:
                QMessageBox.warning(self, "Input Error", "Please fill the brand field.")
        else:
            QMessageBox.warning(self, "Selection Error", "No bus selected for update.")

    def clear_inputs(self):
        self.matricule_input.clear()
        self.tp_input.clear()
        self.brand_input.clear()
        self.selected_matricule = None


class BusCRUDApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Bus CRUD Application")
        self.layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget(self)

        self.create_page = CreatePage(self.load_buses)
        self.list_page = ListPage(self.load_buses, self.switch_to_update)
        self.update_page = UpdatePage(self.load_buses)

        self.stacked_widget.addWidget(self.list_page)
        self.stacked_widget.addWidget(self.create_page)
        self.stacked_widget.addWidget(self.update_page)

        self.layout.addWidget(self.stacked_widget)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Bus")
        self.create_button.clicked.connect(self.show_create_page)
        nav_layout.addWidget(self.create_button)

        self.list_button = QPushButton("List Buses")
        self.list_button.clicked.connect(self.show_list_page)
        nav_layout.addWidget(self.list_button)

        self.layout.addLayout(nav_layout)
        self.setLayout(self.layout)

    def load_buses(self):
        self.list_page.load_buses()

    def switch_to_update(self, matricule):
        self.update_page.load_bus(matricule)
        self.stacked_widget.setCurrentWidget(self.update_page)

    def show_create_page(self):
        self.stacked_widget.setCurrentWidget(self.create_page)

    def show_list_page(self):
        self.stacked_widget.setCurrentWidget(self.list_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BusCRUDApp()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
