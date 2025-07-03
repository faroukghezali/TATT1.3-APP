import sqlite3
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
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


def create_database():
    conn = sqlite3.connect("tatt.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bus (
            matricule TEXT PRIMARY KEY,
            brand_id INTEGER,
            FOREIGN KEY (brand_id) REFERENCES brands (id)
        )
        """
    )
    conn.commit()
    conn.close()


class CreatePage(QWidget):
    def __init__(self, load_bus_callback):
        super().__init__()
        self.load_bus_callback = load_bus_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.matricule_input = QLineEdit(self)
        self.matricule_input.setPlaceholderText("Matricule (Primary Key)")
        layout.addWidget(self.matricule_input)

        self.brand_input = QLineEdit(self)
        self.brand_input.setPlaceholderText("Brand Name")
        layout.addWidget(self.brand_input)

        self.add_brand_button = QPushButton("Add Brand", self)
        self.add_brand_button.clicked.connect(self.add_brand)
        layout.addWidget(self.add_brand_button)

        self.add_button = QPushButton("Add Bus", self)
        self.add_button.clicked.connect(self.add_bus)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def add_brand(self):
        brand_name = self.brand_input.text()
        if brand_name:
            conn = sqlite3.connect("tatt.db")
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO brands (name) VALUES (?)",
                    (brand_name,),
                )
                conn.commit()
                QMessageBox.information(self, "Success", "Brand added successfully.")
                self.brand_input.clear()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Input Error", "Brand name must be unique.")
            conn.close()
        else:
            QMessageBox.warning(
                self, "Input Error", "Please fill the brand name field."
            )

    def add_bus(self):
        matricule = self.matricule_input.text()
        brand_name = self.brand_input.text()

        if matricule and brand_name:
            conn = sqlite3.connect("tatt.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM brands WHERE name=?", (brand_name,))
            brand = cursor.fetchone()

            if brand:
                brand_id = brand[0]
                try:
                    cursor.execute(
                        "INSERT INTO bus (matricule, brand_id) VALUES (?, ?)",
                        (matricule, brand_id),
                    )
                    conn.commit()
                    QMessageBox.information(self, "Success", "Bus added successfully.")
                except sqlite3.IntegrityError:
                    QMessageBox.warning(
                        self, "Input Error", "Matricule must be unique."
                    )
            else:
                QMessageBox.warning(
                    self, "Input Error", "Brand does not exist. Please add it first."
                )
            conn.close()
            self.load_bus_callback()
            self.matricule_input.clear()
            self.brand_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")


class UpdatePage(QWidget):
    def __init__(self, load_bus_callback):
        super().__init__()
        self.load_bus_callback = load_bus_callback
        self.initUI()
        self.selected_matricule = None

    def initUI(self):
        layout = QVBoxLayout()

        self.matricule_input = QLineEdit(self)
        self.matricule_input.setPlaceholderText("Matricule (Primary Key)")
        self.matricule_input.setReadOnly(True)  # Matricule should not be editable
        layout.addWidget(self.matricule_input)

        self.brand_combo = QComboBox(self)  # ComboBox for brand selection
        layout.addWidget(self.brand_combo)

        self.update_button = QPushButton("Update Bus", self)
        self.update_button.clicked.connect(self.update_bus)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def load_bus(self, matricule):
        self.selected_matricule = matricule
        conn = sqlite3.connect("tatt.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bus WHERE matricule=?", (matricule,))
        bus = cursor.fetchone()

        if bus:
            self.matricule_input.setText(bus[0])  # Set matricule
            self.load_brands()  # Load brands into the combo box
            self.brand_combo.setCurrentText(
                self.get_brand_name(bus[1])
            )  # Set selected brand

    def load_brands(self):
        self.brand_combo.clear()  # Clear existing items
        conn = sqlite3.connect("tatt.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM brands")
        brands = cursor.fetchall()
        for brand in brands:
            self.brand_combo.addItem(brand[0])  # Add brand names to the combo box
        conn.close()

    def get_brand_name(self, brand_id):
        conn = sqlite3.connect("tatt.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM brands WHERE id=?", (brand_id,))
        brand = cursor.fetchone()
        conn.close()
        return brand[0] if brand else ""

    def update_bus(self):
        if self.selected_matricule:
            brand_name = self.brand_combo.currentText()

            if brand_name:
                conn = sqlite3.connect("tatt.db")
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM brands WHERE name=?", (brand_name,))
                brand = cursor.fetchone()

                if brand:
                    brand_id = brand[0]
                    cursor.execute(
                        "UPDATE bus SET brand_id=? WHERE matricule=?",
                        (brand_id, self.selected_matricule),
                    )
                    conn.commit()
                    conn.close()
                    self.load_bus_callback()
                    QMessageBox.information(
                        self, "Success", "Bus updated successfully."
                    )
                    self.clear_inputs()
                else:
                    QMessageBox.warning(
                        self, "Input Error", "Selected brand does not exist."
                    )
            else:
                QMessageBox.warning(self, "Input Error", "Please select a brand.")
        else:
            QMessageBox.warning(self, "Selection Error", "No bus selected for update.")

    def clear_inputs(self):
        self.matricule_input.clear()
        self.brand_combo.clear()
        self.selected_matricule = None


class ListPage(QWidget):
    def __init__(self, load_bus_callback, switch_to_update_callback):
        super().__init__()
        self.load_bus_callback = load_bus_callback
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
        self.load_bus()

    def load_bus(self):
        self.bus_list.clear()
        conn = sqlite3.connect("tatt.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT bus.matricule, brands.name 
            FROM bus 
            LEFT JOIN brands ON bus.brand_id = brands.id
            """
        )
        bus = cursor.fetchall()
        for bus in bus:
            self.bus_list.addItem(
                f"{bus[0]} - {bus[1]}"
            )  # Display matricule and brand name
        conn.close()

    def load_selected_bus(self, item):
        self.selected_matricule = item.text().split(" - ")[0]

    def delete_bus(self):
        if hasattr(self, "selected_matricule"):
            conn = sqlite3.connect("tatt.db")
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM bus WHERE matricule=?", (self.selected_matricule,)
            )
            conn.commit()
            conn.close()
            self.load_bus()
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


class BusCRUDApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Bus CRUD Application")
        self.layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget(self)

        self.create_page = CreatePage(self.load_bus)
        self.list_page = ListPage(self.load_bus, self.switch_to_update)
        self.update_page = UpdatePage(self.load_bus)

        self.stacked_widget.addWidget(self.list_page)
        self.stacked_widget.addWidget(self.create_page)
        self.stacked_widget.addWidget(self.update_page)

        self.layout.addWidget(self.stacked_widget)

        nav_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Bus")
        self.create_button.clicked.connect(self.show_create_page)
        nav_layout.addWidget(self.create_button)

        self.list_button = QPushButton("List bus")
        self.list_button.clicked.connect(self.show_list_page)
        nav_layout.addWidget(self.list_button)

        self.layout.addLayout(nav_layout)
        self.setLayout(self.layout)

    def load_bus(self):
        self.list_page.load_bus()

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
