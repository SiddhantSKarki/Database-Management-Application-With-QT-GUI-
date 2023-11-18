from PySide2 import QtCore, QtWidgets, QtGui
import mysql.connector
import sys


class DatabaseLoader(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()
    
    def setupUI(self):
        self.resize(2400,1600)
        self.setWindowTitle("DatabaseLoader")
        self.tableWidget = QtWidgets.QTableWidget()
        section = QtWidgets.QGridLayout()
        for i in range(5):
            self.label = QtWidgets.QLabel(f"CheckBox{i}")
            self.checkBox = QtWidgets.QCheckBox()
            section.addWidget(self.label, 0, i, 0 , 3)
            section.addWidget(self.checkBox, 0, i, 0 , 2)



        # continue from here, plan to make things look more like amazon's website


        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.tableWidget, 0, 0)
        layout.addLayout(section, 0, 1)

        layout.setColumnStretch(0, 4)
        layout.setColumnStretch(3, 1)

        self.connect_to_database()

        self.load_data_from_database()

        self.show()
    

    def connect_to_database(self):
        self.db = mysql.connector.connect(
            user='root',
            password='Clfa5ae692._',
            database='bikestore',
            host='localhost'
        )

        self.cur = self.db.cursor()
    
    def load_data_from_database(self):
        query = "SELECT * FROM customers"
        self.cur.execute(query)
        # print(self.cur.description)
        column_names = [row[0] for row in self.cur.description]
        self.tableWidget.setColumnCount(len(column_names))
        self.tableWidget.setHorizontalHeaderLabels(column_names)


        row_num = 0
        for row_data in self.cur:
            self.tableWidget.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.tableWidget.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(data)))
            row_num += 1
    

    def closeEvent(self, event):
        self.db.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = DatabaseLoader()
    sys.exit(app.exec_())
