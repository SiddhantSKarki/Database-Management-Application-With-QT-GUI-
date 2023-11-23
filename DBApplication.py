import typing
from PySide2 import QtGui, QtCore, QtWidgets
import PySide2.QtWidgets
import mysql.connector
import sys
import os
import json

class DBApplication(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        serifFont = QtGui.QFont("Times", 10, QtGui.QFont.Monospace)
        self.setFont(serifFont)
        self.tables = ['customers', 'categories', 'order_items',
                       'orders', 'products']
        self._table_func_map = {
            "CUSTOMERS" : self.customer_form,
            "CATEGORIES" : self.categories_form,
            "ORDER_ITEMS": self.order_items_form,
            "ORDERS": self.orders_form,
            "PRODUCTS" : self.products_form,
        }
        # Define all the components
        self.content_manager()
        self.layout_manager()
        self.comp_assembler()



        #add each component into a layout
    def content_manager(self):
        self.load_btn = QtWidgets.QPushButton("Load")
        self.select_label = QtWidgets.QLabel("Select Database")
        self.dropdown = QtWidgets.QComboBox()

        self.load_btn.clicked.connect(self.magic)
        self.read_database()

        # FOR dropdown
        for table in self.tables:
            self.dropdown.addItem(table.upper())
        
    def read_database(self):
        config_dir = os.path.join("..", "config.json")
        with open(config_dir, mode='+r',newline='\n') as file:
            json_file = json.load(file)
        user = json_file['mysql']['user']
        pswd = json_file['mysql']['password']
        host = json_file['mysql']['host']
        database = json_file['mysql']['database']
        self.db = mysql.connector.connect(
            user=user,
            password=pswd,
            database=database,
            host=host
        )
        self.cur = self.db.cursor()

    def layout_manager(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.sub_layout = QtWidgets.QGridLayout()
        self.dummy_layout = QtWidgets.QGridLayout()
        self.form_layout = None
    
    def comp_assembler(self):
        self.main_layout.addLayout(self.dummy_layout)
        self.dummy_layout.addWidget(self.select_label, 0 , 0, QtCore.Qt.AlignRight)
        self.dummy_layout.addWidget(self.dropdown, 0 , 1, QtCore.Qt.AlignCenter)
        self.dummy_layout.addWidget(self.load_btn, 0, 2, QtCore.Qt.AlignLeft)
        self.dummy_layout.setColumnStretch(0, 2)
        self.dummy_layout.setColumnStretch(2, 2)
        self.main_layout.addLayout(self.sub_layout)

        self.sub_layout.setColumnStretch(0, 3)

        self.message_label = QtWidgets.QLabel(f"Data not Loaded")
        self.main_layout.addWidget(self.message_label, alignment=QtCore.Qt.AlignBottom)


    def magic(self):
        self.setup_data()
        row_num = 0
        column_headers = [column[0] for column in self.cur.description]
        self.db_table.setColumnCount(len(column_headers))
        self.db_table.setHorizontalHeaderLabels(column_headers)
        for row in self.cur:
            self.db_table.insertRow(row_num)
            for col, col_data in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.db_table.setItem(row_num, col, item)
            row_num += 1
        self.message_label.setText(f"{row_num} records found")
        self.form_select(self.dropdown.currentText())
        self.sub_layout.addWidget(self.db_table, 0, 0)
        self.db.close()

    def clear_layout(self, layout: QtWidgets.QLayout):
        while layout.count():
            item = layout.takeAt(0)
            if isinstance(item, QtWidgets.QLayout):
                self.clear_layout(item)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def form_select(self, table):
        if self.form_layout:
            self.clear_layout(self.form_layout)
        self.form_layout = QtWidgets.QFormLayout()
        self.sub_layout.addLayout(self.form_layout, 0, 1)
        self.form_title_1 = QtWidgets.QLabel("Customers Search Options")
        self.form_layout.addWidget(self.form_title_1)
        self._table_func_map["CUSTOMERS"]()
        self.form_title_2 = QtWidgets.QLabel("Orders Search Options")
        self.form_layout.addWidget(self.form_title_2)
        self._table_func_map["ORDERS"]()
        self._table_func_map["ORDER_ITEMS"]()
        self.form_title_3 = QtWidgets.QLabel("Products Search Options")
        self.form_layout.addWidget(self.form_title_3)
        self._table_func_map["PRODUCTS"]()
        self.submit_button = QtWidgets.QPushButton("Submit")
        self.form_layout.addRow(self.submit_button)
        

    def customer_form(self):
        self.form_last_name = QtWidgets.QLabel("Last Name:")
        self.form_first_name = QtWidgets.QLabel("First Name: ")
        self.state_label = QtWidgets.QLabel("State:")
        self.zip_code = QtWidgets.QLabel("Zip Code: ")
        self.field_first_name = QtWidgets.QLineEdit()
        self.field_last_name = QtWidgets.QLineEdit()
        self.field_state = QtWidgets.QLineEdit()

        self.field_first_name.setFixedHeight(30)
        self.field_last_name.setFixedHeight(30)
        self.field_state.setFixedHeight(30)
        self.field_state.setFixedHeight(30)

        self.form_layout.addRow(self.form_first_name, self.field_first_name)
        self.form_layout.addRow(self.form_last_name, self.field_last_name)
        self.form_layout.addRow(self.state_label, self.field_state)
    
    def categories_form(self):

        self.form_category = QtWidgets.QLabel("Category:")
        self.form_cat_id = QtWidgets.QLabel("Category ID: ")
        self.field_category = QtWidgets.QLineEdit()
        self.field_cat_id = QtWidgets.QLineEdit()
        

        self.field_category.setFixedHeight(30)
        self.field_cat_id.setFixedHeight(30)
        
        self.form_layout.addRow(self.form_category, self.field_category)
        self.form_layout.addRow(self.form_cat_id , self.field_cat_id)

    def order_items_form(self):
        self.quantity = QtWidgets.QLabel("Quantity:")
        self.discount = QtWidgets.QLabel("Discount(%):")

        self.max_quantity = QtWidgets.QLineEdit()
        self.min_quantity = QtWidgets.QLineEdit()

        self.max_dis = QtWidgets.QLineEdit()
        self.min_dis = QtWidgets.QLineEdit()

        self.quantity_max_min = QtWidgets.QHBoxLayout()
        self.quantity_max_min.addWidget(QtWidgets.QLabel("MIN"))
        self.quantity_max_min.addWidget(self.min_quantity)
        self.quantity_max_min.addWidget(QtWidgets.QLabel("MAX"))
        self.quantity_max_min.addWidget(self.max_quantity)

        self.discount_max_min = QtWidgets.QHBoxLayout()
        self.discount_max_min.addWidget(QtWidgets.QLabel("MIN"))
        self.discount_max_min.addWidget(self.min_dis)
        self.discount_max_min.addWidget(QtWidgets.QLabel("MAX"))
        self.discount_max_min.addWidget(self.max_dis)

        self.min_quantity.setFixedWidth(40)
        self.max_quantity.setFixedWidth(40)

        self.min_dis.setFixedWidth(40)
        self.max_dis.setFixedWidth(40)

        self.form_layout.addRow(self.quantity, self.quantity_max_min)
        self.form_layout.addRow(self.discount, self.discount_max_min)


    def orders_form(self):
        self.order_status_label = QtWidgets.QLabel("Order Status:")
        self.required_date_label = QtWidgets.QLabel("Required Date:")
        self.shipped_date_label = QtWidgets.QLabel("Shipped Date:")

        self.field_order_status = QtWidgets.QLineEdit()
        self.field_required_date = QtWidgets.QLineEdit()
        self.field_shipped_date = QtWidgets.QLineEdit()

        for field in [self.field_order_status,
                    self.field_required_date, self.field_shipped_date]:
            field.setFixedHeight(30)
        
        self.form_layout.addRow(self.order_status_label, self.field_order_status)
        self.form_layout.addRow(self.required_date_label, self.field_required_date)
        self.form_layout.addRow(self.shipped_date_label, self.field_shipped_date)


    def products_form(self):
        self.form_title = QtWidgets.QLabel("Products Search Options")

        self.product_name_label = QtWidgets.QLabel("Product Name:")
        self.brand_name_label = QtWidgets.QLabel("Brand Name:")
        self.category_name_label = QtWidgets.QLabel("Category Name:")
        self.model_year_label = QtWidgets.QLabel("Model Year:")
        self.list_price_label = QtWidgets.QLabel("List Price:")

        self.field_product_name = QtWidgets.QLineEdit()
        self.field_brand_name = QtWidgets.QLineEdit()
        self.field_category_name = QtWidgets.QLineEdit()
        self.field_model_year = QtWidgets.QLineEdit()

        self.min_list_price = QtWidgets.QLineEdit()
        self.max_list_price = QtWidgets.QLineEdit()
        self.list_price_max_min = QtWidgets.QHBoxLayout()
        self.list_price_max_min.addWidget(QtWidgets.QLabel("Min:"))
        self.list_price_max_min.addWidget(self.min_list_price)
        self.list_price_max_min.addWidget(QtWidgets.QLabel("Max:"))
        self.list_price_max_min.addWidget(self.max_list_price)
        self.min_list_price.setFixedWidth(40)
        self.max_list_price.setFixedWidth(40)

        for field in [self.field_product_name, self.field_brand_name,
                        self.field_category_name, self.field_model_year]:
            field.setFixedHeight(30)

        self.form_layout.addRow(self.product_name_label, self.field_product_name)
        self.form_layout.addRow(self.brand_name_label, self.field_brand_name)
        self.form_layout.addRow(self.category_name_label, self.field_category_name)
        self.form_layout.addRow(self.model_year_label, self.field_model_year)
        self.form_layout.addRow(self.list_price_label, self.list_price_max_min)
 
    def setup_data(self):
        self.db_table = QtWidgets.QTableWidget()
        try:
            self.read_database()
            query = f"SELECT * FROM bikestore.{self.dropdown.currentText()}"
            self.cur.execute(query)
        except Exception as e:
            print(e.__cause__)

if __name__== '__main__':
    application = QtWidgets.QApplication(sys.argv)

    widget = DBApplication()
    widget.resize(1600, 800)
    widget.show()
    sys.exit(application.exec_())
