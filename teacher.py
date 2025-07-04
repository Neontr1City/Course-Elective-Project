# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'teacher.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import os
from config import UI_CONFIG


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 800)
        # 获取当前脚本所在目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        res_dir = os.path.join(base_dir, "res")
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.background = QtWidgets.QLabel(self.frame)
        self.background.setGeometry(QtCore.QRect(0, 0, 792, 792))
        self.background.setText("")
        self.background.setPixmap(QtGui.QPixmap(os.path.join(res_dir, "背景.png")))
        self.background.setObjectName("background")
        self.return_2 = QtWidgets.QPushButton(self.frame)
        self.return_2.setGeometry(QtCore.QRect(30, 630, 120, 35))
        self.return_2.setObjectName("return_2")
        self.return_2.setStyleSheet(UI_CONFIG['component_styles']['button'])
        self.confirm = QtWidgets.QPushButton(self.frame)
        self.confirm.setGeometry(QtCore.QRect(600, 630, 120, 35))
        self.confirm.setObjectName("confirm")
        self.confirm.setStyleSheet(UI_CONFIG['component_styles']['button'])
        self.teacher_show = QtWidgets.QTextBrowser(self.frame)
        self.teacher_show.setGeometry(QtCore.QRect(140, 190, 521, 491))
        self.teacher_show.setObjectName("teacher_show")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(250, 50, 300, 80))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 3px solid #000000;
                border-radius: 20px;
                padding: 15px 25px;
                font-family: '楷体';
                font-size: 32px;
                font-weight: bold;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #f8f8f8;
                border-color: #2196F3;
            }
        """)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.return_2.setText(_translate("Dialog", "返回"))
        self.confirm.setText(_translate("Dialog", "确认"))
        self.pushButton_2.setText(_translate("Dialog", "必修课老师推荐"))
