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


class CreateCategoryPage(QWidget):
    def __init__(self, load_categories_callback):
        super().__init__()
        self.load_categories_callback = load_categories_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Category Name (Unique)")
        layout.addWidget(self.name_input)

        self.add_button = QPushButton("Add Category", self)
        self.add_button.clicked.connect(self.add_category)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def add_category(self):
        name = self.name_input.text()

        if name:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO category (name) VALUES (?)",
                    (name,),
                )
                conn.commit()
                QMessageBox.information(self, "Success", "Category added successfully.")
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self, "Input Error", "Category name must be unique."
                )
            conn.close()
            self.load_categories_callback()
            self.name_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill the category name.")


class ListCategoryPage(QWidget):
    def __init__(self, load_categories_callback, switch_to_update_callback):
        super().__init__()
        self.load_categories_callback = load_categories_callback
        self.switch_to_update_callback = switch_to_update_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.category_list = QListWidget(self)
        self.category_list.itemClicked.connect(self.load_selected_category)
        layout.addWidget(self.category_list)

        self.delete_button = QPushButton("Delete Category", self)
        self.delete_button.clicked.connect(self.delete_category)
        layout.addWidget(self.delete_button)

        self.update_button = QPushButton("Update Category", self)
        self.update_button.clicked.connect(self.switch_to_update)
        layout.addWidget(self.update_button)

        self.setLayout(layout)
        self.load_categories()

    def load_categories(self):
        self.category_list.clear()
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()
        for category in categories:
            self.category_list.addItem(
                f"{category[0]} - {category[1]}"
            )  # Display id and name
        conn.close()

    def load_selected_category(self, item):
        self.selected_id = item.text().split(" - ")[0]

    def delete_category(self):
        if hasattr(self, "selected_id"):
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM category WHERE id=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.load_categories()
            QMessageBox.information(self, "Success", "Category deleted successfully.")
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a category to delete."
            )

    def switch_to_update(self):
        if hasattr(self, "selected_id"):
            self.switch_to_update_callback(self.selected_id)
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a category to update."
            )


class UpdateCategoryPage(QWidget):
    def __init__(self, load_categories_callback):
        super().__init__()
        self.load_categories_callback = load_categories_callback
        self.initUI()
        self.selected_id = None

    def initUI(self):
        layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Category Name")
        layout.addWidget(self.name_input)

        self.update_button = QPushButton("Update Category", self)
        self.update_button.clicked.connect(self.update_category)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def load_category(self, category_id):
        self.selected_id = category_id
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM category WHERE id=?", (category_id,))
        category = cursor.fetchone()
        conn.close()

        if category:
            self.name_input.setText(category[1])  # Set category name

    def update_category(self):
        if self.selected_id:
            name = self.name_input.text()

            if name:
                conn = sqlite3.connect("main.db")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE category SET name=? WHERE id=?",
                    (name, self.selected_id),
                )
                conn.commit()
                conn.close()
                self.load_categories_callback()
                QMessageBox.information(
                    self, "Success", "Category updated successfully."
                )
                self.clear_inputs()
            else:
                QMessageBox.warning(
                    self, "Input Error", "Please fill the category name."
                )
        else:
            QMessageBox.warning(
                self, "Selection Error", "No category selected for update."
            )

    def clear_inputs(self):
        self.name_input.clear()
        self.selected_id = None


class CreateProductPage(QWidget):
    def __init__(self, load_products_callback, load_categories_callback):
        super().__init__()
        self.load_products_callback = load_products_callback
        self.load_categories_callback = load_categories_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Product Name")
        layout.addWidget(self.name_input)

        self.quantity_input = QLineEdit(self)
        self.quantity_input.setPlaceholderText("Quantity")
        layout.addWidget(self.quantity_input)

        self.price_input = QLineEdit(self)
        self.price_input.setPlaceholderText("Price")
        layout.addWidget(self.price_input)

        self.sku_input = QLineEdit(self)
        self.sku_input.setPlaceholderText("Product SKU")
        layout.addWidget(self.sku_input)

        self.category_combo = QComboBox(self)
        layout.addWidget(self.category_combo)

        self.add_button = QPushButton("Add Product", self)
        self.add_button.clicked.connect(self.add_product)
        layout.addWidget(self.add_button)

        self.setLayout(layout)
        self.load_categories()

    def load_categories(self):
        self.category_combo.clear()
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()
        for category in categories:
            self.category_combo.addItem(f"{category[1]}", category[0])
        conn.close()

    def add_product(self):
        name = self.name_input.text()
        quantity = self.quantity_input.text()
        price = self.price_input.text()
        sku = self.sku_input.text()
        category_id = self.category_combo.currentData()

        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO product (name, quantity, price,sku, category_id) VALUES (?, ?, ?, ?,?)",
            (name, int(quantity), float(price), sku, category_id),
        )
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success", "Product added successfully.")
        self.load_products_callback()
        self.name_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.sku_input.clear()


class ListProductPage(QWidget):
    def __init__(self, load_products_callback, switch_to_update_callback):
        super().__init__()
        self.load_products_callback = load_products_callback
        self.switch_to_update_callback = switch_to_update_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.product_list = QListWidget(self)
        self.product_list.itemClicked.connect(self.load_selected_product)
        layout.addWidget(self.product_list)

        self.delete_button = QPushButton("Delete Product", self)
        self.delete_button.clicked.connect(self.delete_product)
        layout.addWidget(self.delete_button)

        self.update_button = QPushButton("Update Product", self)
        self.update_button.clicked.connect(self.switch_to_update)
        layout.addWidget(self.update_button)

        self.setLayout(layout)
        self.load_products()

    def load_products(self):
        self.product_list.clear()
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product.name,product.quantity,product.price,category.name,product.id\
                        FROM product JOIN category ON category.id = product.category_id;"
        )
        products = cursor.fetchall()
        for product in products:
            self.product_list.addItem(
                f"{product[4]} - {product[0]} - {product[1]} - {product[2]} - {product[3]}"
            )
        conn.close()

    def load_selected_product(self, item):
        self.selected_id = item.text().split(" - ")[0]

    def delete_product(self):
        if hasattr(self, "selected_id"):
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM product WHERE name=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.load_products()
            QMessageBox.information(self, "Success", "Product deleted successfully.")
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a product to delete."
            )

    def switch_to_update(self):
        print("switch to update")
        if hasattr(self, "selected_id"):
            print("has att inside",self.selected_id)
            self.switch_to_update_callback(self.selected_id)
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a product to update."
            )


class UpdateProductPage(QWidget):
    def __init__(self, load_products_callback):
        super().__init__()
        self.load_products_callback = load_products_callback
        self.initUI()
        self.selected_id = None

    def initUI(self):
        layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Product Name")
        layout.addWidget(self.name_input)

        self.quantity_input = QLineEdit(self)
        self.quantity_input.setPlaceholderText("Quantity")
        layout.addWidget(self.quantity_input)

        self.price_input = QLineEdit(self)
        self.price_input.setPlaceholderText("Price")
        layout.addWidget(self.price_input)

        self.sku_input = QLineEdit(self)
        self.sku_input.setPlaceholderText("Product SKU")
        layout.addWidget(self.sku_input)

        self.category_combo = QComboBox(self)
        layout.addWidget(self.category_combo)

        self.update_button = QPushButton("Update Product", self)
        self.update_button.clicked.connect(self.update_product)
        layout.addWidget(self.update_button)

        self.setLayout(layout)
        self.load_categories()

    def load_categories(self):
        self.category_combo.clear()
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()
        for category in categories:
            self.category_combo.addItem(
                f"{category[1]}", category[0]
            )  # Display name, store id
        conn.close()

    def load_product(self, product_id):
        self.selected_id = product_id
        conn = sqlite3.connect("main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id=?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        print(f"the loaded product is {product}")

        if product:
            self.name_input.setText(product[1])  # Set product name
            self.quantity_input.setText(str(product[2]))  # Set quantity
            self.price_input.setText(str(product[3]))  # Set price
            self.sku_input.setText(str(product[4]))  # Set price
            self.category_combo.setCurrentIndex(
                self.category_combo.findData(product[5])
            )  # Set category

    def update_product(self):
        if self.selected_id:
            name = self.name_input.text()
            quantity = self.quantity_input.text()
            price = self.price_input.text()
            category_id = self.category_combo.currentData()
            sku = self.sku_input.text()

            if name and quantity.isdigit() and price.replace(".", "", 1).isdigit():
                conn = sqlite3.connect("main.db")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE product SET name=?, quantity=?, price=?,sku=?, category_id=? WHERE id=?",
                    (name, int(quantity), float(price),sku, category_id, self.selected_id),
                )
                conn.commit()
                conn.close()
                self.load_products_callback()
                QMessageBox.information(
                    self, "Success", "Product updated successfully."
                )
                self.clear_inputs()
            else:
                QMessageBox.warning(
                    self, "Input Error", "Please fill all fields correctly."
                )
        else:
            QMessageBox.warning(
                self, "Selection Error", "No product selected for update."
            )

    def clear_inputs(self):
        self.name_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.category_combo.setCurrentIndex(-1)
        self.selected_id = None


class ProductCRUDApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Product CRUD Application")
        self.layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget(self)

        # Create pages
        self.create_category_page = CreateCategoryPage(self.load_categories)
        self.list_category_page = ListCategoryPage(
            self.load_categories, self.switch_to_update_category
        )
        self.update_category_page = UpdateCategoryPage(self.load_categories)

        self.create_product_page = CreateProductPage(
            self.load_products, self.load_categories
        )
        self.list_product_page = ListProductPage(
            self.load_products, self.switch_to_update_product
        )
        self.update_product_page = UpdateProductPage(self.load_products)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.list_category_page)
        self.stacked_widget.addWidget(self.create_category_page)
        self.stacked_widget.addWidget(self.update_category_page)

        self.stacked_widget.addWidget(self.list_product_page)
        self.stacked_widget.addWidget(self.create_product_page)
        self.stacked_widget.addWidget(self.update_product_page)

        self.layout.addWidget(self.stacked_widget)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.create_category_button = QPushButton("Create Category")
        self.create_category_button.clicked.connect(self.show_create_category_page)
        nav_layout.addWidget(self.create_category_button)

        self.list_category_button = QPushButton("List Categories")
        self.list_category_button.clicked.connect(self.show_list_category_page)
        nav_layout.addWidget(self.list_category_button)

        self.create_product_button = QPushButton("Create Product")
        self.create_product_button.clicked.connect(self.show_create_product_page)
        nav_layout.addWidget(self.create_product_button)

        self.list_product_button = QPushButton("List Products")
        self.list_product_button.clicked.connect(self.show_list_product_page)
        nav_layout.addWidget(self.list_product_button)

        self.layout.addLayout(nav_layout)
        self.setLayout(self.layout)

    def load_categories(self):
        self.list_category_page.load_categories()

    def load_products(self):
        self.list_product_page.load_products()

    def switch_to_update_category(self, category_id):
        self.update_category_page.load_category(category_id)
        self.stacked_widget.setCurrentWidget(self.update_category_page)

    def switch_to_update_product(self, product_id):
        self.update_product_page.load_product(product_id)
        self.stacked_widget.setCurrentWidget(self.update_product_page)

    def show_create_category_page(self):
        self.stacked_widget.setCurrentWidget(self.create_category_page)

    def show_list_category_page(self):
        self.stacked_widget.setCurrentWidget(self.list_category_page)

    def show_create_product_page(self):
        self.stacked_widget.setCurrentWidget(self.create_product_page)

    def show_list_product_page(self):
        self.stacked_widget.setCurrentWidget(self.list_product_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductCRUDApp()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
