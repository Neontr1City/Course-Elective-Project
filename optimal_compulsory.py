# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import os
from extract_courses import get_optional_compulsory_courses, has_time_conflict
from config import UI_CONFIG

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(900, 800)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        res_dir = os.path.join(base_dir, "res")
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        # 背景图片
        self.background = QtWidgets.QLabel(self.frame)
        self.background.setGeometry(QtCore.QRect(-360, -40, 1928, 2503))
        self.background.setObjectName("background")
        # 加载背景图片（如有）
        try:
            background_path = os.path.join(base_dir, "res", "背景.png")
            if os.path.exists(background_path):
                self.background.setPixmap(QtGui.QPixmap(background_path))
        except Exception as e:
            print(f"加载背景图片失败: {e}")

        # 标题
        self.title_label = QtWidgets.QPushButton(self.frame)
        self.title_label.setGeometry(QtCore.QRect(250, 50, 300, 80))
        self.title_label.setObjectName("title_label")
        self.title_label.setText("选择性必修课选择")
        self.title_label.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 3px solid #000000;
                border-radius: 20px;
                padding: 15px 25px;
                font-family: '楷体';
                font-size: 24px;         
                font-weight: bold;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #f8f8f8;
                border-color: #2196F3;
            }
        """)

        # 课程表格
        self.list = QtWidgets.QTableWidget(self.frame)
        self.list.setGeometry(QtCore.QRect(30, 150, 350, 450))
        self.list.setObjectName("list")
        self.list.setColumnCount(3)
        self.list.setHorizontalHeaderLabels(['课程名称', '课程时间', '学分数'])
        self.list.setStyleSheet(UI_CONFIG['component_styles']['table'])
        self.list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.list.horizontalHeader().setStretchLastSection(True)
        self.list.verticalHeader().setVisible(False)
        self.list.setColumnWidth(0, 180)
        self.list.setColumnWidth(1, 100)
        self.list.setColumnWidth(2, 60)

        # 右侧复选框区域（滚动）
        self.layoutWidget = QtWidgets.QWidget(self.frame)
        self.layoutWidget.setGeometry(QtCore.QRect(400, 150, 280, 450))
        self.layoutWidget.setObjectName("layoutWidget")
        self.scrollArea = QtWidgets.QScrollArea(self.layoutWidget)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 280, 450))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: 2px solid #000000;
                border-radius: 10px;
                background-color: #ffffff;
            }
        """)
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollArea.setWidget(self.scrollWidget)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")

        # 累计学分显示区域
        self.pushButton_4 = QtWidgets.QPushButton(self.frame)
        self.pushButton_4.setGeometry(QtCore.QRect(280, 620, 241, 51))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet(UI_CONFIG['component_styles']['credits_display']['background'])

        self.all_points = QtWidgets.QLCDNumber(self.frame)
        self.all_points.setGeometry(QtCore.QRect(380, 620, 141, 51))
        self.all_points.setObjectName("all_points")
        self.all_points.setStyleSheet(UI_CONFIG['component_styles']['credits_display']['lcd'])
        self.all_points.setDigitCount(4)
        self.all_points.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(290, 630, 78, 23))
        self.label.setObjectName("label")
        self.label.setText("已选学分")
        self.label.setStyleSheet(UI_CONFIG['component_styles']['credits_display']['label'])

        # 底部按钮
        self.back = QtWidgets.QPushButton(self.frame)
        self.back.setGeometry(QtCore.QRect(60, 700, 120, 40))
        self.back.setObjectName("back")
        self.back.setText("返回")
        self.back.setStyleSheet(UI_CONFIG['component_styles']['button'])

        self.confirm = QtWidgets.QPushButton(self.frame)
        self.confirm.setGeometry(QtCore.QRect(700, 700, 120, 40))
        self.confirm.setObjectName("confirm")
        self.confirm.setText("确认")
        self.confirm.setStyleSheet(UI_CONFIG['component_styles']['button'])

        # 设置z-order
        self.background.raise_()
        self.layoutWidget.raise_()
        self.pushButton_4.raise_()
        self.confirm.raise_()
        self.list.raise_()
        self.all_points.raise_()
        self.back.raise_()
        self.label.raise_()
        self.title_label.raise_()

        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

class OptimalCompulsoryUi(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, grade, major, compulsory_courses=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.grade = grade
        self.major = major
        self.compulsory_courses = compulsory_courses or []
        self.selected_courses = []
        self.checkboxes = []
        self.load_courses()
        self.confirm.clicked.connect(self.confirm_selection)
        self.back.clicked.connect(self.reject)

    def load_courses(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            res_dir = os.path.join(base_dir, "res")
            file_path = os.path.join(res_dir, "通班&智能专业课 表格.xlsx")
            courses = get_optional_compulsory_courses(file_path, self.grade, self.major)
            self.list.setRowCount(len(courses))
            # 清空旧复选框
            for cb in self.checkboxes:
                cb.deleteLater()
            self.checkboxes.clear()
            # 填充表格和复选框
            from main_enhanced import user_data
            selected_names = set()
            for c in user_data.get("optional_compulsory_courses", []):
                if "name" in c:
                    selected_names.add(c["name"])
                elif "课程名称" in c:
                    selected_names.add(c["课程名称"])
            # 填充表格和复选框
            for i, course in enumerate(courses):
                # 表格
                name_item = QtWidgets.QTableWidgetItem(course['课程名称'])
                time_item = QtWidgets.QTableWidgetItem(str(course['上课时间']))
                credit_item = QtWidgets.QTableWidgetItem(str(course['学分']))
                for item in (name_item, time_item, credit_item):
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.list.setItem(i, 0, name_item)
                self.list.setItem(i, 1, time_item)
                self.list.setItem(i, 2, credit_item)
                # 复选框
                checkbox = QtWidgets.QCheckBox(f"{course['课程名称']}（{course['学分']}分）", self.scrollWidget)
                checkbox.setProperty('course_data', course)
                checkbox.stateChanged.connect(self.update_selection)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 16px;           /* 字体更大 */
                        font-weight: bold;
                        color: #222;
                        padding: 8px 12px;
                        background: #F5F5F5;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        transition: background 0.2s;
                    }
                    QCheckBox:hover {
                        background: #E0E0E0;
                    }
                    QCheckBox:checked {
                        font-weight: bold;
                        color: #2196F3;
                        background: #E3F2FD;
                        border: 2px solid #2196F3;
                        box-shadow: 0 2px 8px rgba(33,150,243,0.15);
                    }
                """)
                # 优先根据user_data恢复勾选
                if course['课程名称'] in selected_names:
                    checkbox.setChecked(True)
                self.verticalLayout.addWidget(checkbox)
                self.checkboxes.append(checkbox)
            self.list.resizeColumnsToContents()
            self.list.resizeRowsToContents()
            self.update_selection()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"加载课程数据失败：{str(e)}")
            import traceback
            traceback.print_exc()

    def update_selection(self):
        self.selected_courses = []
        current_selection_credits = 0
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                course_data = checkbox.property('course_data')
                if course_data:
                    self.selected_courses.append(course_data)
                    current_selection_credits += float(course_data['学分'])
        # 只加必修课学分（不加已累计的选择性必修课学分）
        from main_enhanced import user_data
        compulsory_credits = sum(course['credit'] for course in user_data.get('compulsory_courses', []))
        total_display_credits = compulsory_credits + current_selection_credits
        self.all_points.display(total_display_credits)
        self.label.setText(f"累积学分 (当前选择{len(self.selected_courses)}门)")

    def confirm_selection(self):
        if not self.selected_courses:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少选择一门课程")
            return
        if self.check_time_conflicts():
            QtWidgets.QMessageBox.warning(self, "警告", "所选课程存在时间冲突，请重新选择")
            return
        try:
            from main_enhanced import user_data
            formatted_optional = []
            for course in self.selected_courses:
                formatted_optional.append({
                    'name': course.get('课程名称', ''),
                    'credit': float(course.get('学分', 0)),
                    'time': course.get('上课时间', ''),
                    'location': course.get('上课地点', ''),
                    'teacher': course.get('教师', ''),
                    'course_type': '选择性必修课'
                })
            user_data["optional_compulsory_courses"] = formatted_optional
            optional_credits = sum(course['credit'] for course in formatted_optional)
            user_data["total_credits"] += optional_credits
            
            # 跳转到通识课选择
            from optimal import OptimalDialog
            optimal_dialog = OptimalDialog(self.grade, self.major)
            self.accept()
            optimal_result = optimal_dialog.exec_()
            
            # 如果用户从通识课界面返回，重新显示选择性必修课界面
            if optimal_result == QtWidgets.QDialog.Rejected:
                print("用户从通识课界面返回，重新显示选择性必修课界面")
                # 重新创建选择性必修课界面
                new_optimal_compulsory = OptimalCompulsoryUi(self.grade, self.major)
                new_optimal_compulsory.exec_()
                
        except Exception as e:
            print(f"保存选择性必修课数据时出错: {e}")
            import traceback
            traceback.print_exc()

    def check_time_conflicts(self):
        for i in range(len(self.selected_courses)):
            for j in range(i + 1, len(self.selected_courses)):
                if has_time_conflict(
                    self.selected_courses[i]['上课时间'],
                    self.selected_courses[j]['上课时间']
                ):
                    return True
        return False

    def get_selected_courses(self):
        return self.selected_courses