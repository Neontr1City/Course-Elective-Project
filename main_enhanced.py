import sys
import os
import requests
import json
import logging
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtWidgets import QMessageBox, QApplication
from config import UI_CONFIG, APP_CONFIG, get_api_key, is_api_configured

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置高DPI支持
if APP_CONFIG['high_dpi_enabled']:
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

# 导入所有UI界面
from welcome import Ui_Dialog as WelcomeUi
from age import Ui_Dialog as AgeUi
from major import Ui_Dialog as MajorUi
from extract_courses import get_compulsory_courses, get_optional_compulsory_courses
from compulsory_choose import CompulsoryChooseUi
from optimal_compulsory import OptimalCompulsoryUi
from optimal import OptimalDialog
from teacher import Ui_Dialog as TeacherUi
from evaluation import Ui_Dialog as EvaluationUi
from final import FinalDialog as FinalDialogClass
from course_rating import course_rating_manager

# 全局用户数据
user_data = {
    "age": None,
    "major": None,
    "compulsory_courses": [],
    "optional_compulsory_courses": [],
    "general_courses": [],
    "total_credits": 0,
    "all_selected_courses": []
}

class AnimatedDialog(QtWidgets.QDialog):
    """带有动画效果的对话框基类"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowTitle(APP_CONFIG['name'])
        
    def showEvent(self, event):
        super().showEvent(event)
        self.fade_in()
        
    def fade_in(self):
        """淡入动画"""
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(UI_CONFIG['animation']['fade_duration'])
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def get_button_style(self, color_key='primary'):
        """获取按钮样式"""
        return UI_CONFIG['component_styles']['button']

class WelcomeDialog(AnimatedDialog):
    def __init__(self):
        super().__init__()
        self.ui = WelcomeUi()
        self.ui.setupUi(self)
        
        # 应用统一样式
        self.setStyleSheet(UI_CONFIG['component_styles']['dialog'])
        self.ui.pushButton.setStyleSheet(UI_CONFIG['component_styles']['button'])
        
        self.setup_animations()
        self.ui.pushButton.clicked.connect(self.goto_age)

    def setup_animations(self):
        """设置按钮悬停动画"""
        self.ui.pushButton.enterEvent = self.button_enter
        self.ui.pushButton.leaveEvent = self.button_leave
        
    def button_enter(self, event):
        """按钮悬停进入"""
        pass  # 样式已在CSS中定义
        
    def button_leave(self, event):
        """按钮悬停离开"""
        pass  # 样式已在CSS中定义

    def goto_age(self):
        self.accept()

class AgeDialog(AnimatedDialog):
    def __init__(self):
        super().__init__()
        self.ui = AgeUi()
        self.ui.setupUi(self)
        
        # 应用统一样式
        self.setStyleSheet(UI_CONFIG['component_styles']['dialog'])
        
        self.setup_buttons()
        self.selected_age = None
        # 绑定返回按钮
        if hasattr(self.ui, 'pushButton'):
            self.ui.pushButton.clicked.connect(self.reject)
        elif hasattr(self.ui, 'pushButton_2'):
            self.ui.pushButton_2.clicked.connect(self.reject)

    def setup_buttons(self):
        """设置年级选择按钮"""
        buttons = [
            (self.ui.one, "大一"),
            (self.ui.two, "大二"), 
            (self.ui.three, "大三"),
            (self.ui.pushButton_6, "大四")
        ]
        
        for button, age in buttons:
            button.clicked.connect(lambda checked, a=age: self.select_age(a))
            button.setStyleSheet(UI_CONFIG['component_styles']['button'])
            
        self.ui.confirm.clicked.connect(self.goto_major)
        self.ui.confirm.setStyleSheet(UI_CONFIG['component_styles']['button'])

    def select_age(self, age):
        self.selected_age = age
        user_data["age"] = age
        # 添加选择反馈
        QMessageBox.information(self, "选择确认", f"您选择了：{age}")

    def goto_major(self):
        if self.selected_age:
            self.accept()
        else:
            QMessageBox.warning(self, "提示", "请先选择年级！")

class MajorDialog(AnimatedDialog):
    def __init__(self):
        super().__init__()
        self.ui = MajorUi()
        self.ui.setupUi(self)
        # 应用统一样式
        self.setStyleSheet(UI_CONFIG['component_styles']['dialog'])
        self.setup_buttons()
        self.selected_major = None
        # 只绑定pushButton_9为返回按钮
        if hasattr(self.ui, 'pushButton_9'):
            self.ui.pushButton_9.clicked.connect(self.reject)

    def setup_buttons(self):
        """设置专业选择按钮"""
        buttons = [
            (self.ui.electronic, "电子信息与技术"),
            (self.ui.information, "信息与计算科学"),
            (self.ui.pushButton_5, "智能科学与技术"),
            (self.ui.yingyongwuli, "应用物理学"),
            (self.ui.computer, "计算机科学与技术"),
            (self.ui.tong, "通班")
        ]
        
        for button, major in buttons:
            button.clicked.connect(lambda checked, m=major: self.select_major(m))
            button.setStyleSheet(UI_CONFIG['component_styles']['button'])
            
        self.ui.pushButton_8.clicked.connect(self.confirm_major)
        self.ui.pushButton_8.setStyleSheet(UI_CONFIG['component_styles']['button'])

    def select_major(self, major):
        self.selected_major = major
        user_data["major"] = major
        QMessageBox.information(self, "选择确认", f"您选择了：{major}")

    def confirm_major(self):
        if self.selected_major:
            self.accept()
        else:
            QMessageBox.warning(self, "提示", "请先选择专业！")

class TeacherDialog(AnimatedDialog):
    def __init__(self, selected_courses=None):
        super().__init__()
        self.ui = TeacherUi()
        self.ui.setupUi(self)
        self.selected_courses = selected_courses or []
        
        # 应用统一样式
        self.setStyleSheet(UI_CONFIG['component_styles']['dialog'])
        
        self.setup_ui()
        self.generate_teacher_recommendations()

    def setup_ui(self):
        """设置UI样式"""
        # 应用统一样式到所有组件
        if hasattr(self.ui, 'pushButton'):
            self.ui.pushButton.setStyleSheet(UI_CONFIG['component_styles']['button'])
        if hasattr(self.ui, 'pushButton_2'):
            self.ui.pushButton_2.setStyleSheet(UI_CONFIG['component_styles']['button'])
        if hasattr(self.ui, 'textBrowser'):
            self.ui.textBrowser.setStyleSheet(UI_CONFIG['component_styles']['text_browser'])
        
        # 连接按钮信号
        if hasattr(self.ui, 'pushButton'):
            self.ui.pushButton.clicked.connect(self.accept)
        if hasattr(self.ui, 'pushButton_2'):
            self.ui.pushButton_2.clicked.connect(self.reject)

    def generate_teacher_recommendations(self):
        """生成教师推荐"""
        try:
            if not self.selected_courses:
                content = """
                <h2 style='color: #2196F3; font-family: 楷体;'>📚 教师推荐</h2>
                <p style='font-family: 楷体;'>暂无选课信息，无法提供教师推荐。</p>
                """
            else:
                course_names = [course.get('课程名称', '') for course in self.selected_courses if course.get('课程名称')]
                recommendations = course_rating_manager.get_teacher_recommendations(course_names)
                
                content = "<h2 style='color: #2196F3; font-family: 楷体;'>📚 必修课教师推荐</h2>"
                
                if not recommendations:
                    content += "<p style='font-family: 楷体;'>暂时没有教师推荐数据。</p>"
                else:
                    for course_name, rec_info in recommendations.items():
                        content += f"<h3 style='color: #333; font-family: 楷体;'>📖 {course_name}</h3>"
                        
                        if rec_info['status'] == 'success':
                            teacher = rec_info['recommended_teacher']
                            score_info = rec_info['score_info']
                            
                            content += f"""
                            <div style='margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: 楷体;'>
                                <p><strong>推荐教师：</strong>{teacher}</p>
                                <p><strong>综合评分：</strong>{score_info['score']:.1f}/10</p>
                                <p><strong>课程平均分：</strong>{score_info['avg_score']:.1f}</p>
                                <p><strong>内容评分：</strong>{score_info['content_score']:.1f}/10</p>
                                <p><strong>评价人数：</strong>{score_info['review_count']}人</p>
                                <p><strong>工作量：</strong>{score_info['workload']}</p>
                            </div>
                            """
                        else:
                            content += f"<p style='color: #666; font-family: 楷体;'>{rec_info['message']}</p>"
                
                # 添加AI辅助推荐
                if course_names:
                    ai_content = self.generate_ai_teacher_recommendation(course_names)
                    content += f"<br><h3 style='color: #FF9800; font-family: 楷体;'>🤖 AI 教师推荐建议</h3>{ai_content}"
            
            if hasattr(self.ui, 'textBrowser'):
                self.ui.textBrowser.setHtml(content)
            
        except Exception as e:
            print(f"生成教师推荐失败: {e}")
            if hasattr(self.ui, 'textBrowser'):
                self.ui.textBrowser.setHtml(f"<p style='font-family: 楷体;'>生成教师推荐时出现错误：{str(e)}</p>")

    def generate_ai_teacher_recommendation(self, course_names):
        """使用AI生成教师推荐建议"""
        try:
            from llm_integration import LLMIntegration
            
            llm = LLMIntegration()
            prompt = f"""
            请为以下必修课程提供选择教师的建议：
            课程列表：{', '.join(course_names)}
            
            请提供：
            1. 选择教师时应该考虑的因素
            2. 如何平衡课程难度和学习效果
            3. 针对不同学习目标的建议
            
            请用简洁明了的中文回答，不超过200字。
            """
            
            response = llm.call_api(prompt)
            if response and response.get('success'):
                return f"<p style='font-family: 楷体;'>{response['content']}</p>"
            else:
                return self.get_fallback_ai_recommendation()
                
        except Exception as e:
            print(f"AI推荐生成失败: {e}")
            return self.get_fallback_ai_recommendation()
    
    def get_fallback_ai_recommendation(self):
        """获取备用AI推荐"""
        return """
        <p style='font-family: 楷体;'>
        选择教师时建议考虑以下因素：<br>
        1. 教学风格是否适合您的学习习惯<br>
        2. 课程评分和学生反馈<br>
        3. 课程工作量与您的时间安排<br>
        4. 教师的专业背景和研究方向<br>
        建议多渠道了解教师信息，选择最适合自己的课程。
        </p>
        """

class EvaluationDialog(AnimatedDialog):
    def __init__(self):
        super().__init__()
        self.ui = EvaluationUi()
        self.ui.setupUi(self)
        self.setup_ui()

    def setup_ui(self):
        """设置评估界面"""
        self.ui.confirm.clicked.connect(self.goto_final_schedule)
        self.ui.back.clicked.connect(self.go_back_to_general_courses)
        
        # 计算并显示正确的总学分
        compulsory_credits = sum(course['credit'] for course in user_data.get("compulsory_courses", []))
        optional_credits = sum(course['credit'] for course in user_data.get("optional_compulsory_courses", []))
        general_credits = sum(course['credit'] for course in user_data.get("general_courses", []))
        total_credits = compulsory_credits + optional_credits + general_credits
        user_data["total_credits"] = total_credits
        
        self.ui.all_points.display(total_credits)
        print(f"AI评估界面学分统计: 必修{compulsory_credits} + 选择性必修{optional_credits} + 通识{general_credits} = {total_credits}")
        
        # 自动生成评估
        QTimer.singleShot(1000, self.generate_evaluation)
    
    def goto_final_schedule(self):
        """跳转到最终课表"""
        try:
            # 创建最终课表界面
            final_dialog = FinalDialog()
            
            # 关闭当前界面并显示最终课表
            self.accept()
            final_dialog.exec_()
            
        except Exception as e:
            print(f"跳转到最终课表失败: {e}")
            QMessageBox.warning(self, "错误", f"无法跳转到最终课表：{str(e)}")
            self.accept()

    def go_back_to_general_courses(self):
        """返回到通识课选择界面"""
        try:
            print("用户从AI评估界面返回，重新显示通识课选择界面")
            # 重新创建通识课选择界面
            from optimal import OptimalDialog
            optimal_dialog = OptimalDialog(user_data.get("age", "大二"), user_data.get("major", "通班"))
            self.reject()  # 关闭当前界面
            optimal_dialog.exec_()
        except Exception as e:
            print(f"返回通识课选择界面失败: {e}")
            self.reject()

    def generate_evaluation(self):
        print("[DEBUG] 生成AI评估时用户信息：", user_data)
        sys.stdout.flush()
        try:
            # 准备评估数据
            evaluation_data = {
                "年级": user_data["age"],
                "专业": user_data["major"],
                "必修课程": [course['name'] for course in user_data["compulsory_courses"]],
                "选择性必修": [course['name'] for course in user_data["optional_compulsory_courses"]],
                "通识课程": [course['name'] for course in user_data["general_courses"]],
                "总学分": user_data["total_credits"]
            }
            
            # 显示加载动画
            self.ui.textBrowser.setHtml("<h2>🤖 正在生成智能评估...</h2><p>请稍候...</p>")
            QApplication.processEvents()
            
            # 调用大语言模型API
            evaluation_result = self.call_llm_api(evaluation_data)
            
            # 显示评估结果
            self.ui.textBrowser.setHtml(evaluation_result)
            
        except Exception as e:
            error_msg = f"""
            <html>
            <body style="font-family: '微软雅黑';">
                <h2 style="color: #f44336;">⚠️ 评估生成失败</h2>
                <p>由于网络或API问题，无法生成智能评估。</p>
                <p>错误信息: {str(e)}</p>
                <h3>📊 基础评估报告</h3>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px;">
                    <p><strong>学生信息：</strong>{user_data["age"]} - {user_data["major"]}</p>
                    <p><strong>已选课程总数：</strong>{len(user_data["compulsory_courses"]) + len(user_data["optional_compulsory_courses"]) + len(user_data["general_courses"])}门</p>
                    <p><strong>总学分：</strong>{user_data["total_credits"]}分</p>
                    <p><strong>课程结构评估：</strong>课程搭配合理，涵盖了必修、选修和通识教育各个方面。</p>
                    <p><strong>建议：</strong>继续保持学习热情，注重理论与实践相结合。</p>
                </div>
            </body>
            </html>
            """
            self.ui.textBrowser.setHtml(error_msg)

    def call_llm_api(self, data):
        """调用大语言模型API进行评估"""
        try:
            # 导入LLM集成模块
            from llm_integration import get_ai_evaluation
            
            # 调用AI评估
            return get_ai_evaluation(data)
            
        except ImportError:
            # 如果无法导入LLM模块，使用原有的模拟响应
            return self._generate_fallback_evaluation(data)
        except Exception as e:
            # 如果API调用失败，返回错误信息和默认评估
            error_msg = f"""
            <html>
            <body style="font-family: '微软雅黑';">
                <h2 style="color: #f44336;">⚠️ AI评估服务暂时不可用</h2>
                <p>API调用出现问题：{str(e)}</p>
                <h3>📊 基础评估报告</h3>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px;">
                    <p><strong>学生信息：</strong>{data["年级"]} - {data["专业"]}</p>
                    <p><strong>已选课程总数：</strong>{len(data["必修课程"]) + len(data["选择性必修"]) + len(data["通识课程"])}门</p>
                    <p><strong>总学分：</strong>{data["总学分"]}分</p>
                    <p><strong>课程结构评估：</strong>课程搭配合理，涵盖了必修、选修和通识教育各个方面。</p>
                    <p><strong>建议：</strong>继续保持学习热情，注重理论与实践相结合。</p>
                </div>
            </body>
            </html>
            """
            return error_msg
    
    def _generate_fallback_evaluation(self, data):
        """生成备用评估报告（当LLM模块不可用时）"""
        # 模拟AI响应
        response = f"""
        <html>
        <head>
            <style>
                body {{ font-family: '微软雅黑'; line-height: 1.6; }}
                .section {{ margin-bottom: 20px; padding: 15px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                .content {{ background-color: #f8f9fa; }}
                .highlight {{ color: #e74c3c; font-weight: bold; }}
                .good {{ color: #27ae60; }}
                .warning {{ color: #f39c12; }}
            </style>
        </head>
        <body>
            <div class="section header">
                <h2>🤖 AI智能选课评估报告</h2>
                <p>基于您的选课情况，我们为您生成了专业的评估报告</p>
            </div>
            
            <div class="section content">
                <h3>📊 基本信息</h3>
                <ul>
                    <li><strong>年级专业：</strong>{data['年级']} {data['专业']}</li>
                    <li><strong>总学分：</strong><span class="highlight">{data['总学分']}分</span></li>
                    <li><strong>选课门数：</strong>{len(data['必修课程']) + len(data['选择性必修']) + len(data['通识课程'])}门</li>
                </ul>
            </div>
            
            <div class="section content">
                <h3>✅ 课程结构分析</h3>
                <p class="good">▪ 课程结构<strong>合理</strong>，必修、选修、通识教育搭配均衡</p>
                <p class="good">▪ 学分分配<strong>适中</strong>，符合学年学习强度要求</p>
                <p class="warning">▪ 建议关注课程时间冲突，合理安排学习计划</p>
            </div>
            
            <div class="section content">
                <h3>🎯 专业发展建议</h3>
                <p>1. <strong>理论基础：</strong>您选择的必修课程能很好地构建专业理论基础</p>
                <p>2. <strong>实践能力：</strong>建议多参与课程实验和项目实践</p>
                <p>3. <strong>知识拓展：</strong>通识课程有助于培养综合素质</p>
            </div>
            
            <div class="section content">
                <h3>📈 学习规划建议</h3>
                <p>• <strong>短期目标：</strong>专注于必修课程的学习，打牢基础</p>
                <p>• <strong>中期目标：</strong>通过选修课程拓展专业视野</p>
                <p>• <strong>长期目标：</strong>结合通识教育，培养全面发展能力</p>
            </div>
            
            <div class="section content">
                <h3>⭐ 综合评分</h3>
                <div style="text-align: center; font-size: 24px;">
                    <span class="good">课程搭配：8.5/10</span><br>
                    <span class="good">学分安排：9.0/10</span><br>
                    <span class="highlight">总体评价：优秀</span>
                </div>
            </div>
        </body>
        </html>
        """
        
        return response

class FinalDialog(FinalDialogClass):
    def __init__(self):
        super().__init__()
        self.setup_final_ui()

    def setup_final_ui(self):
        """设置最终课表界面"""
        # 计算并显示正确的总学分
        compulsory_credits = sum(course['credit'] for course in user_data.get("compulsory_courses", []))
        optional_credits = sum(course['credit'] for course in user_data.get("optional_compulsory_courses", []))
        general_credits = sum(course['credit'] for course in user_data.get("general_courses", []))
        total_credits = compulsory_credits + optional_credits + general_credits
        user_data["total_credits"] = total_credits
        
        print(f"最终课表学分统计: 必修{compulsory_credits} + 选择性必修{optional_credits} + 通识{general_credits} = {total_credits}")
        
        # 重新连接完成按钮，确保程序正确退出
        self.finish_button.clicked.disconnect()  # 断开原有连接
        self.finish_button.clicked.connect(self.finish_and_exit)

    def finish_and_exit(self):
        """完成选课并退出程序"""
        QMessageBox.information(self, "选课完成", "恭喜您完成选课！祝您学习愉快！")
        self.accept()
        # 退出整个应用程序
        QApplication.quit()

    def generate_final_schedule(self):
        print("[DEBUG] 生成最终课表时用户信息：", user_data)
        sys.stdout.flush()
        """生成最终课表 - 课程表格式"""
        # 计算正确的总学分
        compulsory_credits = sum(course['credit'] for course in user_data.get("compulsory_courses", []))
        optional_credits = sum(course['credit'] for course in user_data.get("optional_compulsory_courses", []))
        general_credits = sum(course['credit'] for course in user_data.get("general_courses", []))
        total_credits = compulsory_credits + optional_credits + general_credits
        
        # 更新全局学分数据
        user_data["total_credits"] = total_credits
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: '微软雅黑'; margin: 10px; }}
                .header {{ background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px; text-align: center; }}
                .schedule-table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
                .schedule-table th, .schedule-table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; font-size: 12px; }}
                .schedule-table th {{ background-color: #f2f2f2; font-weight: bold; }}
                .compulsory {{ background-color: #FFE4E1; }}
                .optional {{ background-color: #E0FFFF; }}
                .general {{ background-color: #F0FFF0; }}
                .summary {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 14px; }}
                .course-info {{ font-size: 10px; line-height: 1.2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h3>🎓 {user_data.get('age', '')} {user_data.get('major', '')} 课程表</h3>
                <p>总学分: {total_credits} 分 | 课程数: {len(user_data.get('compulsory_courses', [])) + len(user_data.get('optional_compulsory_courses', [])) + len(user_data.get('general_courses', []))} 门</p>
            </div>
            
            <table class="schedule-table">
                <tr>
                    <th style="width: 80px;">时间</th>
                    <th>周一</th>
                    <th>周二</th>
                    <th>周三</th>
                    <th>周四</th>
                    <th>周五</th>
                </tr>
        """
        
        # 时间段
        time_slots = [
            "8:00-8:45", "8:55-9:40", "10:00-10:45", "10:55-11:40",
            "13:30-14:15", "14:25-15:10", "15:30-16:15", "16:25-17:10",
            "18:30-19:15", "19:25-20:10", "20:20-21:05", "21:15-22:00"
        ]
        
        # 创建课程表矩阵
        schedule_matrix = [["" for _ in range(5)] for _ in range(12)]
        
        # 解析时间并填入课程
        def parse_time_and_fill(courses, course_type, css_class):
            for course in courses:
                time_str = course.get('time', '')
                if not time_str:
                    continue
                    
                try:
                    # 解析时间格式，如 "周一3-4节"
                    if '周' in time_str and '节' in time_str:
                        # 提取星期
                        weekday = -1
                        if '周一' in time_str: weekday = 0
                        elif '周二' in time_str: weekday = 1
                        elif '周三' in time_str: weekday = 2
                        elif '周四' in time_str: weekday = 3
                        elif '周五' in time_str: weekday = 4
                        
                        if weekday >= 0:
                            # 提取节次
                            import re
                            periods = re.findall(r'(\d+)', time_str)
                            for period in periods:
                                period_num = int(period) - 1  # 转换为0-based索引
                                if 0 <= period_num < 12:
                                    course_info = f'<div class="{css_class}"><div class="course-info"><strong>{course["name"]}</strong><br>{course.get("teacher", "")}<br>{course.get("location", "")}<br>{course["credit"]}学分</div></div>'
                                    schedule_matrix[period_num][weekday] = course_info
                except Exception as e:
                    print(f"解析时间失败: {time_str}, 错误: {e}")
        
        # 填入各类课程
        parse_time_and_fill(user_data.get("compulsory_courses", []), "必修课", "compulsory")
        parse_time_and_fill(user_data.get("optional_compulsory_courses", []), "选择性必修课", "optional")
        parse_time_and_fill(user_data.get("general_courses", []), "通识课", "general")
        
        # 生成表格行
        for i, time_slot in enumerate(time_slots):
            html_content += f"<tr><td><strong>第{i+1}节<br>{time_slot}</strong></td>"
            for j in range(5):
                cell_content = schedule_matrix[i][j] if schedule_matrix[i][j] else ""
                html_content += f"<td>{cell_content}</td>"
            html_content += "</tr>"
        
        html_content += """
            </table>
            
            <div class="summary">
                <h4>📊 课程统计</h4>
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <span style="background-color: #FFE4E1; padding: 2px 8px; border-radius: 3px;">必修课</span>
                        {compulsory_count}门 ({compulsory_credits}学分)
                    </div>
                    <div>
                        <span style="background-color: #E0FFFF; padding: 2px 8px; border-radius: 3px;">选择性必修</span>
                        {optional_count}门 ({optional_credits}学分)
                    </div>
                    <div>
                        <span style="background-color: #F0FFF0; padding: 2px 8px; border-radius: 3px;">通识课</span>
                        {general_count}门 ({general_credits}学分)
                    </div>
                </div>
                <p style="text-align: center; margin-top: 10px;"><strong>总计: {total_credits} 学分</strong></p>
            </div>
        </body>
        </html>
        """.format(
            compulsory_count=len(user_data.get("compulsory_courses", [])),
            compulsory_credits=compulsory_credits,
            optional_count=len(user_data.get("optional_compulsory_courses", [])),
            optional_credits=optional_credits,
            general_count=len(user_data.get("general_courses", [])),
            general_credits=general_credits,
            total_credits=total_credits
        )
        
        return html_content

    def finish_selection(self):
        """完成选课"""
        QMessageBox.information(self, "选课完成", "恭喜您完成选课！祝您学习愉快！")
        self.accept()

def run_welcome_flow():
    welcome = WelcomeDialog()
    return welcome.exec_() == QtWidgets.QDialog.Accepted

def run_age_flow():
    age = AgeDialog()
    result = age.exec_()
    if result == QtWidgets.QDialog.Accepted:
        return "ok"
    else:
        return "back_to_welcome"

def run_major_flow():
    major = MajorDialog()
    result = major.exec_()
    if result == QtWidgets.QDialog.Accepted:
        return "ok"
    else:
        return "back_to_age"

def run_full_selection_flow():
    print("[DEBUG] 进入选课流程，当前用户信息：", user_data)
    sys.stdout.flush()
    # 必修课
    while True:
        compulsory = CompulsoryChooseUi(user_data["age"], user_data["major"])
        result = compulsory.exec_()
        if result == QtWidgets.QDialog.Accepted + 1:
            break  # 进入选择性必修课
        elif result == QtWidgets.QDialog.Rejected:
            return "back_to_major"  # 回到专业选择
    # 选择性必修课
    while True:
        optimal_compulsory = OptimalCompulsoryUi(user_data["age"], user_data["major"])
        result = optimal_compulsory.exec_()
        if result == QtWidgets.QDialog.Accepted:
            break  # 进入通识课
        elif result == QtWidgets.QDialog.Rejected:
            return "back_to_compulsory"  # 回到必修课
    # 通识课
    while True:
        optimal = OptimalDialog(user_data["age"], user_data["major"])
        result = optimal.exec_()
        if result == QtWidgets.QDialog.Accepted:
            break  # 进入评估
        elif result == QtWidgets.QDialog.Rejected:
            return "back_to_optimal_compulsory"  # 回到选择性必修课
    # 评估
    while True:
        evaluation = EvaluationDialog()
        result = evaluation.exec_()
        if result == QtWidgets.QDialog.Accepted:
            break  # 进入最终课表
        elif result == QtWidgets.QDialog.Rejected:
            return "back_to_optimal"  # 回到通识课
    # 最终课表
    final = FinalDialog()
    final.exec_()
    return "done"

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QDialog {
            background-color: #f0f0f0;
        }
        QMessageBox {
            background-color: white;
        }
    """)
    try:
        while True:  # 欢迎
            if not run_welcome_flow():
                break
            while True:  # 年级
                age_result = run_age_flow()
                if age_result == "back_to_welcome":
                    break  # 回到欢迎
                while True:  # 专业
                    major_result = run_major_flow()
                    if major_result == "back_to_age":
                        break  # 回到年级
                    # 必修课
                    while True:
                        compulsory = CompulsoryChooseUi(user_data["age"], user_data["major"])
                        result = compulsory.exec_()
                        if result == QtWidgets.QDialog.Accepted + 1:
                            # 进入选择性必修课
                            while True:
                                optimal_compulsory = OptimalCompulsoryUi(user_data["age"], user_data["major"])
                                result2 = optimal_compulsory.exec_()
                                if result2 == QtWidgets.QDialog.Accepted:
                                    # 进入通识课
                                    while True:
                                        optimal = OptimalDialog(user_data["age"], user_data["major"])
                                        result3 = optimal.exec_()
                                        if result3 == QtWidgets.QDialog.Accepted:
                                            # 进入评估
                                            while True:
                                                evaluation = EvaluationDialog()
                                                result4 = evaluation.exec_()
                                                if result4 == QtWidgets.QDialog.Accepted:
                                                    final = FinalDialog()
                                                    final.exec_()
                                                    break  # 选课流程结束
                                                elif result4 == QtWidgets.QDialog.Rejected:
                                                    # 回到通识课
                                                    break
                                            if result4 == QtWidgets.QDialog.Rejected:
                                                continue  # 回到通识课
                                            break  # 评估完成，退出通识课
                                        elif result3 == QtWidgets.QDialog.Rejected:
                                            # 回到选择性必修课
                                            break
                                    if result3 == QtWidgets.QDialog.Rejected:
                                        continue  # 回到选择性必修课
                                    break  # 通识课完成，退出选择性必修课
                                elif result2 == QtWidgets.QDialog.Rejected:
                                    # 回到必修课
                                    break
                            if result2 == QtWidgets.QDialog.Rejected:
                                continue  # 回到必修课
                            break  # 选择性必修课完成，退出必修课
                        elif result == QtWidgets.QDialog.Rejected:
                            # 回到专业选择
                            break
                    if result == QtWidgets.QDialog.Rejected:
                        continue  # 回到专业选择
                    break  # 必修课完成，退出专业选择
    except Exception as e:
        QMessageBox.critical(None, "系统错误", f"系统遇到错误：{str(e)}")
    sys.exit()

if __name__ == "__main__":
    main() 