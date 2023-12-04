from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtGui import QFontDatabase
import PySide6.QtWidgets
import mysql.connector
import sys
import os
import json


class SaveDialog(QtWidgets.QDialog):
    def __init__(self, save_query, app_db):
        """
        A custom QDialog for entering table details.

        Parameters:
            save_query (str): The save query to be executed.
            app_db (DatabaseConnection): An instance of the database connection.
        """
        super().__init__()
        self.query = save_query
        self.cursor = app_db.cursor()
        self.table_name = ""
        QFontDatabase.addApplicationFont("./fonts/montserrat/static/Montserrat-Thin.ttf")
        self.setFont(QtGui.QFont("Montserrat", 12))
        self.resize(800, 200)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.button_layout = QtWidgets.QHBoxLayout()
        self.title = QtWidgets.QLabel("Enter the table details")
        self.main_layout.addWidget(self.title)
        self.table_name_lb = QtWidgets.QLabel("Table Name: ")
        self.table_name_field = QtWidgets.QLineEdit()
        self.form_layout.addRow(self.table_name_lb, self.table_name_field)
        self.main_layout.addLayout(self.form_layout)

        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close_operation)
        save_btn.clicked.connect(self.magic)
        self.button_layout.addWidget(save_btn)
        self.button_layout.addWidget(cancel_btn)

        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)
    

    def magic(self):
        """
        Execute the magic operation to create a new table based on the provided save query.

        This method retrieves the table name from the input field, constructs a CREATE TABLE
        query, and executes it. If an exception occurs during execution, it prints the exception
        message. Finally, it closes the dialog.

        Returns:
            None
        """
        self.table_name = self.table_name_field.text()
        new_query = f"CREATE TABLE {self.table_name} AS " + self.query 
        try:
            # print(new_query)
            self.cursor.execute(new_query)
        except Exception as e:
            print(e)
        self.close_operation()
        
    def close_operation(self):
        self.close()

class DBApplication(QtWidgets.QWidget):

    def __init__(self):
        """
        Constructor method for initializing the main application window.

        This method sets up the main application window with the Montserrat font,
        initializes a list of tables, and creates a mapping between table names and
        their respective form functions. It then calls methods for managing content,
        layout, and assembling components.

        Parameters:
            None

        Attributes:
            tables (list): A list of table names.
            _table_func_map (dict): A mapping between table names
        """
        super().__init__()
        QFontDatabase.addApplicationFont("./fonts/montserrat/static/Montserrat-Regular.ttf")
        self.setFont(QtGui.QFont("Montserrat", 10.5))
        self.tables = ['CUSTOMERS']
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
        """
        Method for managing the content of the main application window.

        This method creates and configures UI components for loading, deleting, and selecting databases.
        It connects the load and delete buttons to their respective functions and calls methods for
        reading the database and resetting the dropdown.

        Parameters: None
        """
        self.load_btn = QtWidgets.QPushButton("Load")
        self.drop_btn = QtWidgets.QPushButton("Delete")
        self.select_label = QtWidgets.QLabel("Select Database")

        self.load_btn.clicked.connect(self.querySelectionLoad)
        self.drop_btn.clicked.connect(self.drop_table)
        self.read_database()
        self.reset_dropdown()
       
    

    def reset_dropdown(self):
        """
        Method for resetting the dropdown menu with table names.

        This method creates a QComboBox for displaying table names and initializes it with
        existing tables and dynamically created tables. It reads the existing tables from a file
        and adds them to the dropdown. It also checks for dynamically created tables and adds them.

        Parameters:
            None
        """
         # FOR dropdown
        self.dropdown = QtWidgets.QComboBox()
        for table in self.tables:
            self.dropdown.addItem(table.upper())
        self.created_tables = []
        with open("./bin/tables.bin", mode='r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip('\n')
                if line:
                    if  line not in self.tables:
                        self.created_tables.append(line)
                        self.dropdown.addItem(line)

    def drop_table(self):
        """
        Method for dropping a selected table.

        This method retrieves the current selection from the dropdown, checks if it's a dynamically
        created table, removes it from the list of created tables, updates the file containing table names,
        removes the table from the dropdown, and executes the drop query. If the selected table is a standard
        table, it raises an exception indicating no permission to delete standard tables.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception: Raised when attempting to delete standard tables.
        """
        curr = self.dropdown.currentText()
        if curr not in self.tables:
            # print(curr)
            self.created_tables.remove(curr)
            with open("./bin/tables.bin", mode ='w') as file:
                for line in self.created_tables:
                    line = line + '\n'
                    file.write(line)  
            current_index = self.dropdown.currentIndex()
            self.dropdown.removeItem(current_index)
            # self.clear_table()
            self.drop_query(curr)
        else:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Permission Denied")
            msg_box.setText(f"Permission Denied to delete main table {curr}")
            msg_box.exec()
        
    def drop_query(self, table_name):
        """
        Executes a query to drop the specified table.

        Parameters:
            table_name (str): The name of the table to be dropped.

        Returns:
            None
        """
        self.read_database()
        temp_cur = self.db.cursor()
        try:
            temp_cur.execute(f"DROP TABLE {table_name};")
        except Exception as e:
            print(e.__cause__)
        self.db.close()
        
    def read_database(self):
        """
        Reads database configuration from a JSON file and establishes a MySQL connection.

        Parameters:
            None

        Returns:
            None
        """
        config_dir = os.path.join(".", "config.json")
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
        """
    Manages the layout of the main application window.

    Parameters:
        None

    Returns:
        None
    """
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.sub_layout = QtWidgets.QGridLayout()
        self.dummy_layout = QtWidgets.QGridLayout()
        self.form_layout = None
    
    def comp_assembler(self):
        """
        Assembles and adds UI components to the main application window layout.

        Parameters:
            None

        Returns:
            None
        """
        self.main_layout.addLayout(self.dummy_layout)
        self.dummy_layout.addWidget(self.select_label, 0 , 0, QtCore.Qt.AlignRight)
        self.dummy_layout.addWidget(self.dropdown, 0 , 1, QtCore.Qt.AlignCenter)
        self.dummy_layout.addWidget(self.load_btn, 0, 2, QtCore.Qt.AlignLeft)
        self.dummy_layout.addWidget(self.drop_btn, 0, 3, QtCore.Qt.AlignLeft)
        self.dummy_layout.setColumnStretch(0, 2)
        self.dummy_layout.setColumnStretch(3, 2)
        self.main_layout.addLayout(self.sub_layout)

        self.sub_layout.setColumnStretch(0, 3)

        self.message_label = QtWidgets.QLabel(f"Data not Loaded")
        self.main_layout.addWidget(self.message_label, alignment=QtCore.Qt.AlignBottom)


    def form_select(self, table):
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
            self.clear_btn = QtWidgets.QPushButton("Clear")
            self.clear_btn.clicked.connect(self.clear)
            self.order = QtWidgets.QComboBox()
            self.order.addItem("ASC")
            self.order.addItem("DESC")
            self.form_layout.addRow(QtWidgets.QLabel("Order"), self.order)
            self.form_layout.addRow(QtWidgets.QLabel(""))
            self.horizontal = QtWidgets.QHBoxLayout()
            self.horizontal.addWidget(self.submit_button)
            self.horizontal.addWidget(self.clear_btn)
            self.form_layout.addRow(self.clear_btn, self.submit_button)
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
        try:
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
        except Exception as e:
            msgBox = QtWidgets.QMessageBox();
            msgBox.setText("Error: " + str(e.__cause__));
            msgBox.setWindowTitle("Error")
            msgBox.exec();



    def save_magic(self):
        newItem = ""
        self.read_database()
        dialog = SaveDialog(self.query, self.db)
        dialog.exec()
        newItem = dialog.table_name
        if newItem != "":
            self.dropdown.addItem(newItem)
            self.created_tables.append(newItem)
            with open("./bin/tables.bin", 'ab') as file:
                file.write(newItem.encode() + b'\n')
        self.db.close()

    def check_dict_contents(self, form_dict, form_name):
        isEmpty = True
        cols = []
        for key,value in form_dict.items():
            if isinstance(value, QtWidgets.QLineEdit):
                if value.text() != '':
                    isEmpty = False
            else:
                if value[0].text() != '' or value[1].text() != '':
                    isEmpty = False
            cols.append(f"{form_name}.{key}")
        return (isEmpty,cols)
    

    def where_mod(self, form_dict, form_name):
        """
        Constructs a WHERE clause component for a SQL query based on the provided form data.

        Parameters:
            form_dict (dict): A dictionary containing form field names as keys and their corresponding
                            QtWidgets.QLineEdit or tuple of QLineEdits as values.
            form_name (str): The name of the form or table to be used in the WHERE clause.

        Returns:
            str: A string representing the WHERE clause component for the SQL query.

        Notes:
            The method iterates through the form fields in the given dictionary and checks whether
            the field values are provided. For single-line edit fields, it adds conditions to the WHERE
            clause based on the data type of the field. For range-based fields (e.g., quantity, discount),
            it checks for provided minimum and maximum values to construct a range condition.

            Numeric fields (e.g., quantity, discount, list_price) are considered for sorting options
            and added to the sort_options QComboBox if not already present.

            The constructed WHERE clause component is returned as a string.
        """
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
        """
        Generates and executes a SQL query based on user input in various form fields.

        This method constructs a SELECT query for retrieving data from the database tables (CUSTOMERS, ORDERS, ORDER_ITEMS, PRODUCTS)
        based on the user's input in form fields. It builds the JOIN and WHERE clauses dynamically and includes sorting options.
  
        If the "Save to Database" button is clicked, it connects to the `save_magic` method to save the query results.

        Parameters:
            None

        Returns:
            None
        """
        if not self.save_button:
            self.save_button = QtWidgets.QPushButton("Save to Database")
            self.save_button.clicked.connect(self.save_magic)
        self.form_layout.addRow(self.save_button)
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

        # print(self.query)
        self.magic()

    def querySelectionLoad(self):
        self.query = f"SELECT * FROM bikestore.{self.dropdown.currentText()}"
        self.magic()

    def setup_data(self):
        self.db_table = QtWidgets.QTableWidget()
        self.read_database()
        self.cur.execute(self.query)

    def clear_layout(self, layout: QtWidgets.QLayout):
        while layout.count():
            item = layout.takeAt(0)
            if isinstance(item, QtWidgets.QLayout):
                self.clear_layout(item)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    def clear(self):
        self.clear_layout(self.form_layout)
        self.sub_layout.removeItem(self.form_layout)
        self.form_layout = None
        self.form_select(self.db_table)

if __name__== '__main__':
    application = QtWidgets.QApplication(sys.argv)

    widget = DBApplication()
    widget.resize(1300, 700)
    widget.show()
    sys.exit(application.exec())