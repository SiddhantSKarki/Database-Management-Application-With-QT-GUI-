from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import QFontDatabase
import PySide2.QtWidgets
import mysql.connector
import sys
import os
import json

class DBApplication(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        QFontDatabase.addApplicationFont("./montserrat/static/Montserrat-Regular.ttf")
        # self.setStyleSheet("background-color: rgb(255, 165, 0);")
        self.setFont(QtGui.QFont("Montserrat", 10.5))
        self.tables = ['customers', 'order_items',
                       'orders', 'products']
        self._table_func_map = {
            "CUSTOMERS" : self.customer_form,
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

        self.load_btn.clicked.connect(self.querySelectionLoad)
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


    def form_select(self, table): #TODO: Remove the table parameter if not necessary
        if not self.form_layout:
            self.form_layout = QtWidgets.QFormLayout()
            self.sub_layout.addLayout(self.form_layout, 0, 1)
            self.form_title_1 = QtWidgets.QLabel("Customers Search Options")
            self.form_layout.addWidget(self.form_title_1)
            self._table_func_map["CUSTOMERS"]()
            self.form_title_2 = QtWidgets.QLabel("Orders Search Options")
            self.form_layout.addWidget(self.form_title_2)
            self._table_func_map["ORDERS"]()
            self._table_func_map["ORDER_ITEMS"]()
            self._table_func_map["PRODUCTS"]()
            self.submit_button = QtWidgets.QPushButton("Submit")
            self.submit_button.clicked.connect(self.querySelection)
            self.sort_label = QtWidgets.QLabel("Sort by: ")
            self.sort_options = QtWidgets.QComboBox()
            self.sort_options.addItem("customer_id")
            self.sort_options.addItem("first_name")
            self.sort_options.addItem("last_name")
            self.form_layout.addWidget(QtWidgets.QLabel("Additional Options"))
            self.form_layout.addRow(self.sort_label, self.sort_options)
            self.order = QtWidgets.QComboBox()
            self.order.addItem("ASC")
            self.order.addItem("DESC")
            self.form_layout.addRow(QtWidgets.QLabel("Order"), self.order)
            self.form_layout.addRow(QtWidgets.QLabel(""))
            self.form_layout.addWidget(self.submit_button)
            self._customers_query_dict = {
                'first_name':self.field_first_name,
                'last_name':self.field_last_name,
                'state':self.field_state
            }
            self._orders_query_dict = {
                'order_status':self.field_order_status,
                'shipped_date':self.field_shipped_date,
                'required_date':self.field_required_date
            }
            self._oitems_query_dict = {
                'discount' : (self.min_dis, self.max_dis),
                'quantity' : (self.min_quantity, self.max_quantity)
            }
            self._products_query_dict = {
                'product_name': self.field_product_name,
                'list_price' : (self.min_list_price, self.max_list_price),
                'model_year': self.field_model_year
            }
            self.save_button = None
            self.sort_option_list = []

    def customer_form(self):
        self.form_last_name = QtWidgets.QLabel("Last Name:")
        self.form_first_name = QtWidgets.QLabel("First Name: ")
        self.state_label = QtWidgets.QLabel("State:")
        self.field_first_name = QtWidgets.QLineEdit()
        self.field_last_name = QtWidgets.QLineEdit()
        self.field_state = QtWidgets.QLineEdit()

        self.field_first_name.setFixedHeight(30)
        self.field_last_name.setFixedHeight(30)
        self.field_state.setFixedHeight(30)

        self.form_layout.addRow(self.form_first_name, self.field_first_name)
        self.form_layout.addRow(self.form_last_name, self.field_last_name)
        self.form_layout.addRow(self.state_label, self.field_state)

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
        self.form_title_3 = QtWidgets.QLabel("Products Search Options")

        self.product_name_label = QtWidgets.QLabel("Product Name:")
        self.model_year_label = QtWidgets.QLabel("Model Year:")
        self.list_price_label = QtWidgets.QLabel("List Price:")

        self.field_product_name = QtWidgets.QLineEdit()
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


        for field in [self.field_product_name, self.field_model_year]:
            field.setFixedHeight(30)
        self.form_layout.addWidget(self.form_title_3)
        self.form_layout.addRow(self.product_name_label, self.field_product_name)
        self.form_layout.addRow(self.model_year_label, self.field_model_year)
        self.form_layout.addRow(self.list_price_label, self.list_price_max_min)
 
    def magic(self):
        self.setup_data()
        row_num = 0
        self.column_headers = [column[0] for column in self.cur.description]
        self.db_table.setColumnCount(len(self.column_headers))
        self.db_table.setHorizontalHeaderLabels(self.column_headers)
        for row in self.cur:
            self.db_table.insertRow(row_num)
            for col, col_data in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.db_table.setItem(row_num, col, item)
            row_num += 1
            
        self.message_label.setText(f"{row_num} records found")
        self.sub_layout.addWidget(self.db_table, 0, 0)
        self.form_select(self.db_table)
        self.db.close()

    def save_magic(self):
        pass

    def check_dict_contents(self, form_dict, form_name):
        isEmpty = True
        cols = []
        for key,value in form_dict.items():
            if isinstance(value, QtWidgets.QLineEdit):
                if value.text() != '':
                    isEmpty = False
                    cols.append(f"{form_name}.{key}")
            else:
                if value[0].text() != '' or value[1].text() != '':
                    isEmpty = False
                    cols.append(f"{form_name}.{key}")
        return (isEmpty,cols)
    
    def where_mod(self, form_dict, form_name):
        where_component = ""
        for key, value in form_dict.items():
                if isinstance(value, QtWidgets.QLineEdit):
                    if value.text() != '':
                        if self.num > 0:
                            where_component += " AND "
                        else:
                            where_component += " WHERE "
                        if key == 'order_status':
                            where_component += f"{form_name}.{key} = {value.text()}"
                        elif key == 'required_date' or key == 'shipped_date' or key == 'model_year':
                            where_component += f"{form_name}.{key} = '{value.text()}'"
                        elif key == 'first_name' or key == 'last_name' or key == "product_name" or key == 'state':
                            where_component += f"{form_name}.{key} LIKE '{value.text()}%'"
                        self.num+=1
                else:
                    if value[0].text() != '' or value[1].text() != '':
                        if self.num > 0:
                            where_component += " AND "
                        else:
                            where_component += " WHERE "
                        if key == 'quantity' or  key == 'discount' or key == 'list_price':
                            if not(key in self.sort_option_list):
                                self.sort_option_list.append(key)
                                self.sort_options.addItem(key)
                            if value[0].text() != '' and value[1].text() != '':
                                where_component += f"{form_name}.{key} BETWEEN {value[0].text()} AND {value[1].text()}" 
                            elif value[0].text() != '':
                                where_component += f"ABS({form_name}.{key} - {value[0].text()}) < 0.00001 "
                            else:
                                where_component += f"{form_name}.{key} BETWEEN 0 AND {value[1].text()}"
                        self.num+=1
        return where_component
                        

    def querySelection(self):
        if not self.save_button:
            self.save_button = QtWidgets.QPushButton("Save to Database")
        self.form_layout.addRow(self.save_button)
        self.save_button.clicked.connect(self.save_magic)
        self.num = 0
        
        join_component = ""
        where_component = ""
        column_comp = ", ".join([f"CUSTOMERS.{column}" for column in ['customer_id', 'first_name', 'last_name','phone','email','street','city','state','zipcode']])

        customers_form_entry = self.check_dict_contents(self._customers_query_dict, "CUSTOMERS")
        where_component += self.where_mod(self._customers_query_dict, "CUSTOMERS")
        orders_form_entry = self.check_dict_contents(self._orders_query_dict, "ORDERS")
        if not orders_form_entry[0]:
            join_component += " INNER JOIN bikestore.ORDERS ON CUSTOMERS.customer_id = bikestore.ORDERS.customer_id "
            where_component += self.where_mod(self._orders_query_dict, "ORDERS")
            column_comp += "," + ', '.join(orders_form_entry[1])

        oitems_form_entry = self.check_dict_contents(self._oitems_query_dict, "ORDER_ITEMS")
        if not oitems_form_entry[0]:
            if orders_form_entry[0]:
                join_component += " INNER JOIN bikestore.ORDERS ON CUSTOMERS.customer_id = bikestore.ORDERS.customer_id "
            join_component += " INNER JOIN bikestore.ORDER_ITEMS ON ORDER_ITEMS.order_id = bikestore.ORDERS.order_id "
            where_component += self.where_mod(self._oitems_query_dict, "ORDER_ITEMS")
            column_comp += "," + ', '.join(oitems_form_entry[1])

        products_form_entry = self.check_dict_contents(self._products_query_dict, "PRODUCTS")
        if not products_form_entry[0]:
            if oitems_form_entry[0]:
                if orders_form_entry[0]:
                    join_component += " INNER JOIN bikestore.ORDERS ON CUSTOMERS.customer_id = bikestore.ORDERS.customer_id " 
                join_component += " INNER JOIN bikestore.ORDER_ITEMS ON ORDER_ITEMS.order_id = bikestore.ORDERS.order_id "
            join_component += " INNER JOIN bikestore.products ON bikestore.order_items.product_id = bikestore.products.product_id"
            where_component += self.where_mod(self._products_query_dict, "PRODUCTS")
            column_comp += "," + ', '.join(products_form_entry[1])
        query_text = f"SELECT {column_comp} FROM bikestore.CUSTOMERS "

        order_by_comp = f" ORDER BY {self.sort_options.currentText()} {self.order.currentText()};"
        query_text = query_text + join_component + where_component + order_by_comp
        self.query = query_text

        print(self.query)
        self.magic()

    def querySelectionLoad(self):
        self.query = f"SELECT * FROM bikestore.{self.dropdown.currentText()}"
        self.magic()

    def setup_data(self):
        self.db_table = QtWidgets.QTableWidget()
        try:
            self.read_database()
            self.cur.execute(self.query)
        except Exception as e:
            print(e.__cause__)

    def clear_layout(self, layout: QtWidgets.QLayout):
        while layout.count():
            item = layout.takeAt(0)
            if isinstance(item, QtWidgets.QLayout):
                self.clear_layout(item)
            widget = item.widget()
            if widget:
                widget.deleteLater()

if __name__== '__main__':
    application = QtWidgets.QApplication(sys.argv)

    widget = DBApplication()
    widget.resize(1600, 800)
    widget.show()
    sys.exit(application.exec_())