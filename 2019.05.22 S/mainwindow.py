from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication
from tkinter import *
import pyodbc
from datetime import datetime
from PyQt5.QtGui import *

# connection with database:
conn = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    "Server=DESKTOP-O6OPF2T\MISIASQL;"
    "Database=PulsometerDatabase;"
    "Trusted_Connection=yes;")

# variable:
nowid = 0
countlastdata = 0


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi('gui_login.ui', self)
        self.w1 = CreateAccount()
        self.w2 = MesaurementPuls()
        self.b_createaccount.clicked.connect(self.gotocreateaccount)
        self.b_login.clicked.connect(self.checkdata)
        self.widget.setPixmap(QPixmap("pulsoapp.PNG"))
        self.widget.show()

    def checkdata(self):
        login = self.et_login.text()
        password = self.et_password.text()

        if login and password != '':

            cur = conn.cursor()
            query = "select count(login) from dbo.Dane_użytkownika where login = " + "'" + login + "'" + " and password = " + "'" + password + "'" + ";"
            count = cur.execute(query).fetchall()

            cur = conn.cursor()
            query1 = "select id_użytkownika from dbo.Dane_użytkownika where login = " + "'" + login + "'" + " and password = " + "'" + password + "'" + ";"
            id_user = cur.execute(query1).fetchall()

            for row in id_user:
                id_user = row[0]

            for row in count:
                count = row[0]

            if count == 1:
                global nowid
                nowid = id_user
                self.gotomeasurement()

            if count == 0:
                self.messagebox()
            cur.close()

        else:
            self.messagebox_emptyscope()

    def gotocreateaccount(self):
        self.w1.show()

    def gotomeasurement(self):
        self.w2.show()

    def messagebox(self):
        QMessageBox.warning(self, 'Komunikat', 'Podane dane są nieprawidłowe lub nie istnieją w bazie.')

    def messagebox_emptyscope(self):
        QMessageBox.warning(self, 'Komunikat', 'Wszystkie pola muszą być uzupełnione.')


class CreateAccount(QDialog):
    def __init__(self):
        super(CreateAccount, self).__init__()
        loadUi('gui_createaccount.ui', self)
        self.b_create.clicked.connect(self.createaccount)
        self.widget.setPixmap(QPixmap("pulsoapp2.PNG"))
        self.widget.show()

    def createaccount(self):
        newlogin = self.et_putlogin.text()
        newpassword = self.et_putpassword.text()
        repeatpassword = self.et_repeatpassword.text()

        countlogin = len(newlogin)
        countpassword = len(newpassword)

        if newlogin and newpassword and repeatpassword != '':
            if countlogin >= 5:
                if countpassword >= 5:
                    if newpassword == repeatpassword:
                        cur = conn.cursor()
                        query = "select count(login) from dbo.Dane_użytkownika where login = " + "'" + newlogin + "'" + ";"
                        count = cur.execute(query).fetchall()

                        for row in count:
                            count = row[0]

                        if count == 1:
                            self.messagebox_exist()

                        if count == 0:
                            cur = conn.cursor()
                            query1 = "insert into dbo.Dane_użytkownika (login, password) values " + "('" + newlogin + "', '" + newpassword + "')"
                            cur.execute(query1)

                            conn.commit()
                            self.messegebox_good()
                            self.closewindowcreate()

                    else:
                        self.messagebox_notthesamepassword()
                else:
                    self.messagebox_tooshortpassword()
            else:
                self.messagebox_tooshortlogin()
        else:
            self.messagebox_emptyscope()

    def closewindowcreate(self):
        self.destroy()

    # Gotowe komunikaty dotyczące nieprawidłowo podanych danych:

    def messegebox_good(self):
        QMessageBox.warning(self, 'Komunikat', 'Rejestracja przebiegła pomyślnie.')

    def messagebox_exist(self):
        QMessageBox.warning(self, 'Komunikat', 'Taki login już istnieje w bazie.')

    def messagebox_emptyscope(self):
        QMessageBox.warning(self, 'Komunikat', 'Wszystkie pola muszą być uzupełnione.')

    def messagebox_tooshortlogin(self):
        QMessageBox.warning(self, 'Komunikat', 'Podany login jest za krótki. Musi mieć conajmniej 5 znaków.')

    def messagebox_tooshortpassword(self):
        QMessageBox.warning(self, 'Komunikat', 'Podane hasło jest za krótkie. Musi mieć conajmniej 5 znaków')

    def messagebox_notthesamepassword(self):
        QMessageBox.warning(self, 'Komunikat', 'Podane hasła są różne.')


class MesaurementPuls(QDialog):
    def __init__(self):
        super(MesaurementPuls, self).__init__()
        loadUi('gui_measurement.ui', self)
        self.w4 = Data()
        self.b_seeothers.clicked.connect(self.gotodata)
        self.b_start.clicked.connect(self.enabledsavedata)
        self.b_save.clicked.connect(self.savedata)
        self.widget.setPixmap(QPixmap("pulsoapp2.PNG"))
        self.widget.show()

    def gotodata(self):
        self.w4.show()

    def enabledsavedata(self):
        self.b_save.setEnabled(True)

    def savedata(self):
        todaydate = datetime.today().strftime('%Y-%m-%d')
        todaytime = datetime.today().strftime('%H:%M:%S')
        print(todaytime)
        measurevalue = self.l_puls.text()
        iduser = nowid
        cur = conn.cursor()
        query4 = "Insert into dbo.Pomiar(id_użytkownika, value, data, time) values('" + str(
         iduser) + "', '" + measurevalue + "', '" + todaydate + "', '" + todaytime + "')"
        cur.execute(query4)
        conn.commit()

        QMessageBox.warning(self, 'Komunikat',
                            'Pomiar o wartości: ' + measurevalue + ' BPM w dniu: ' + todaydate + ' o godzinie: ' + todaytime +  ' dodano poprawnie.')


class Data(QDialog):
    def __init__(self):
        super(Data, self).__init__()
        loadUi('gui_data.ui', self)
        self.b_show.clicked.connect(self.downloaddata)
        self.widget.setPixmap(QPixmap("pulsoapp2.PNG"))
        self.widget.show()
        choosedata = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        self.l_data.setText(str(choosedata))

        self.d_sort.addItem("-")
        self.d_sort.addItem("data rosnąco")
        self.d_sort.addItem("data malejąco")
        self.d_sort.addItem("najwyższy puls")
        self.d_sort.addItem("najniższy puls")
        self.d_sort.currentIndexChanged.connect(self.sortcombobox)
        self.checkbox_all.clicked.connect(self.showall)

    def sortcombobox(self):
        choosedata = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        print(choosedata)
        combotext = self.d_sort.currentText()
        if combotext == 'data rosnąco' and self.checkbox_all.isChecked():
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar order by data ASC, time ASC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

        if combotext == 'data malejąco' and self.checkbox_all.isChecked():
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar order by data DESC, time DESC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

        if combotext == 'najwyższy puls' and self.checkbox_all.isChecked():
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar order by value DESC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

        if combotext == 'najniższy puls' and self.checkbox_all.isChecked():
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar order by value ASC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

        if combotext == 'data rosnąco' and self.checkbox_all.isChecked() == False:
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar where id_użytkownika = '" + str(
            nowid) + "' and  data = '" + choosedata + "'" + " order by data ASC, time ASC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

        if combotext == 'data malejąco' and self.checkbox_all.isChecked() == False:
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar where id_użytkownika = '" + str(
            nowid) + "' and  data = '" + choosedata + "'" + " order by data DESC, time DESC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

        if combotext == 'najwyższy puls' and self.checkbox_all.isChecked() == False:
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar where id_użytkownika = '" + str(
            nowid) + "' and  data = '" + choosedata + "'" + " order by value DESC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

        if combotext == 'najniższy puls' and self.checkbox_all.isChecked() == False:
            self.listWidget.clear()
            cur = conn.cursor()
            query2 = "select value, data, time from dbo.Pomiar where id_użytkownika = '" + str(
            nowid) + "' and  data = '" + choosedata + "'" + " order by value ASC"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))

    def showall(self):
        if self.checkbox_all.isChecked() == True:
            self.listWidget.clear()
            choosedata = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
            print(choosedata)
            cur = conn.cursor()
            query1 = "select COUNT(value) from dbo.Pomiar"
            count = cur.execute(query1).fetchall()

            for row in count:
                count = row[0]
                print(count)

            if count != 0:
                query2 = "select value, data, time from dbo.Pomiar"
                value = cur.execute(query2).fetchall()

                for row in value:
                    self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))
                    self.l_data.setText(choosedata)

            else:
                self.listWidget.addItem("Brak pomiarów w tym dniu.")
                self.l_data.setText(choosedata)

        if self.checkbox_all.isChecked() == False:
            self.listWidget.clear()

    def downloaddata(self):
        self.listWidget.clear()
        choosedata = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        print(choosedata)
        cur = conn.cursor()
        query1 = "select COUNT(value) from dbo.Pomiar where id_użytkownika = '" + str(
            nowid) + "' and  data = '" + choosedata + "'"
        count = cur.execute(query1).fetchall()

        for row in count:
            count = row[0]
            print(count)

        if count != 0:
            query2 = "select value, data, time from dbo.Pomiar where id_użytkownika = '" + str(
                nowid) + "' and data = '" + choosedata + "'"
            value = cur.execute(query2).fetchall()

            for row in value:
                self.listWidget.addItem(str(row[0]) + " BPM " + str(row[1]) + " " + str(row[2]))
                self.l_data.setText(choosedata)

        else:
            self.listWidget.addItem("Brak pomiarów w tym dniu.")
            self.l_data.setText(choosedata)


app = QApplication(sys.argv)
window = Login()
window.setWindowTitle('PulsoApp')
window.show()
sys.exit(app.exec())
