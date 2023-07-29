import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QPushButton, QWidget, QLineEdit, QLabel, QDialog, QMessageBox


class PasswordManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

        # Initialize the SQLite database and create the "passwords" table
        self.conn = sqlite3.connect('passwords.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                                id INTEGER PRIMARY KEY,
                                account TEXT NOT NULL,
                                username TEXT NOT NULL,
                                password TEXT NOT NULL
                                )''')
        self.conn.commit()

        # Load saved passwords from the database on application startup
        self.load_passwords()

    def init_ui(self):
        self.setWindowTitle('Password Manager')
        self.setGeometry(100, 100, 600, 400)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Account', 'Username', 'Password'])

        self.add_btn = QPushButton('Add Account', self)
        self.add_btn.clicked.connect(self.add_account)

        self.delete_btn = QPushButton('Delete Account', self)
        self.delete_btn.clicked.connect(self.delete_account)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.delete_btn)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_passwords(self):
        # Fetch saved passwords from the database and populate the table
        self.cursor.execute('SELECT * FROM passwords')
        rows = self.cursor.fetchall()

        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, cell_data in enumerate(row_data[1:]):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

    def add_account(self):
        # Show a dialog to add a new account
        account, ok = PasswordDialog.get_account_details(self)
        if ok:
            self.cursor.execute('INSERT INTO passwords (account, username, password) VALUES (?, ?, ?)',
                                (account['account'], account['username'], account['password']))
            self.conn.commit()

            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col_idx, cell_data in enumerate(account.values()):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

    def delete_account(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            account_name = self.table.item(selected_row, 0).text()

            reply = QMessageBox.question(self, 'Confirmation', f'Do you want to delete the account: {account_name}?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.table.removeRow(selected_row)
                self.cursor.execute('DELETE FROM passwords WHERE account = ?', (account_name,))
                self.conn.commit()
        else:
            QMessageBox.warning(self, 'No Account Selected', 'Please select an account to delete.', QMessageBox.Ok)


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.account_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        ok_btn = QPushButton('OK')
        ok_btn.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Account:'))
        layout.addWidget(self.account_input)
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        layout.addWidget(ok_btn)

        self.setLayout(layout)

    @staticmethod
    def get_account_details(parent=None):
        dialog = PasswordDialog(parent)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            return {
                'account': dialog.account_input.text(),
                'username': dialog.username_input.text(),
                'password': dialog.password_input.text(),
            }, True
        else:
            return {}, False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PasswordManagerApp()
    window.show()
    sys.exit(app.exec_())
