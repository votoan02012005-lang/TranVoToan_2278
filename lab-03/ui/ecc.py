# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

# Nếu mở GUI báo lỗi "Qt platform plugin", hãy bỏ comment 2 dòng dưới
# import os
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = "../platforms"

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 380)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.lbl_title = QtWidgets.QLabel(self.centralwidget)
        self.lbl_title.setGeometry(QtCore.QRect(20, 10, 300, 40))
        font = QtGui.QFont(); font.setPointSize(18); font.setBold(True)
        self.lbl_title.setFont(font)
        self.lbl_title.setObjectName("lbl_title")

        self.btn_gen_keys = QtWidgets.QPushButton(self.centralwidget)
        self.btn_gen_keys.setGeometry(QtCore.QRect(340, 15, 140, 30))
        self.btn_gen_keys.setObjectName("btn_gen_keys")

        self.lbl_info = QtWidgets.QLabel(self.centralwidget)
        self.lbl_info.setGeometry(QtCore.QRect(20, 70, 120, 20))
        self.lbl_info.setObjectName("lbl_info")
        self.txt_info = QtWidgets.QTextEdit(self.centralwidget)
        self.txt_info.setGeometry(QtCore.QRect(150, 65, 330, 80))
        self.txt_info.setObjectName("txt_info")

        self.lbl_sign = QtWidgets.QLabel(self.centralwidget)
        self.lbl_sign.setGeometry(QtCore.QRect(20, 165, 120, 20))
        self.lbl_sign.setObjectName("lbl_sign")
        self.txt_sign = QtWidgets.QTextEdit(self.centralwidget)
        self.txt_sign.setGeometry(QtCore.QRect(150, 160, 330, 120))
        self.txt_sign.setObjectName("txt_sign")

        self.btn_sign = QtWidgets.QPushButton(self.centralwidget)
        self.btn_sign.setGeometry(QtCore.QRect(150, 300, 150, 35))
        self.btn_sign.setObjectName("btn_sign")
        self.btn_verify = QtWidgets.QPushButton(self.centralwidget)
        self.btn_verify.setGeometry(QtCore.QRect(330, 300, 150, 35))
        self.btn_verify.setObjectName("btn_verify")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _t = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_t("MainWindow", "ECC Cipher"))
        self.lbl_title.setText(_t("MainWindow", "ECC CIPHER"))
        self.btn_gen_keys.setText(_t("MainWindow", "Generate Keys"))
        self.lbl_info.setText(_t("MainWindow", "Information:"))
        self.lbl_sign.setText(_t("MainWindow", "Signature:"))
        self.btn_sign.setText(_t("MainWindow", "Sign"))
        self.btn_verify.setText(_t("MainWindow", "Verify"))