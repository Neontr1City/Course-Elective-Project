import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView

class TeacherRecommender:
    def __init__(self):
        self.ratings_df = pd.read_excel('res/课程评分.xlsx')
        # 预处理数据
        self._preprocess_data()
    
    def _preprocess_data(self):
        """预处理教师评分数据"""
        # 确保数值列为浮点数类型
        numeric_columns = ['课程内容 满分10分', '课程工作量', '课程考核', '平均分', '有效评价条数']
        for col in numeric_columns:
            self.ratings_df[col] = pd.to_numeric(self.ratings_df[col], errors='coerce').fillna(0)
        
        # 计算综合得分（将所有列的分数加权平均）
        self.ratings_df['综合得分'] = (
            self.ratings_df[['课程内容 满分10分', '课程工作量', '课程考核']].mean(axis=1) * 0.8 +  # 各项评分的平均值
            (self.ratings_df['平均分'] / self.ratings_df['有效评价条数'].replace(0, 1)).fillna(0) * 0.2  # 总分/人数 作为参考
        )
    
    def get_teacher_recommendations(self, course_name: str) -> List[Dict]:
        """获取指定课程的所有教师推荐信息"""
        course_teachers = self.ratings_df[self.ratings_df['课程'] == course_name]
        if course_teachers.empty:
            return []
        
        recommendations = []
        for _, row in course_teachers.iterrows():
            teacher_info = {
                '教师姓名': str(row['老师']),
                '综合得分': float(round(row['综合得分'], 2)),
                '评分人数': int(row['有效评价条数']),
                '教学': float(row['课程内容 满分10分']),
                '给分': float(row['课程工作量']),
                '推荐': float(row['课程考核']),
                '总评分': float(row['平均分']),
                '备注': str(row['数据来源于']) if pd.notna(row['数据来源于']) else ''
            }
            recommendations.append(teacher_info)
        
        # 按综合得分排序
        return sorted(recommendations, key=lambda x: x['综合得分'], reverse=True)

class TeacherRecommendationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recommender = TeacherRecommender()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI界面"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            '教师姓名', '综合得分', '评分人数', 
            '教学评分', '给分评分', '推荐评分',
            '总评分', '备注'
        ])
        
        # 设置表格列宽自适应
        header = self.table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.layout.addWidget(self.table)
        
        # 添加推荐说明标签
        self.recommendation_label = QLabel()
        self.recommendation_label.setWordWrap(True)
        self.layout.addWidget(self.recommendation_label)
    
    def update_recommendations(self, course_name: str):
        """更新教师推荐信息"""
        recommendations = self.recommender.get_teacher_recommendations(course_name)
        
        if not recommendations:
            self.table.setRowCount(0)
            self.recommendation_label.setText("未找到该课程的教师评分信息。")
            return
        
        # 更新表格
        self.table.setRowCount(len(recommendations))
        for row, teacher in enumerate(recommendations):
            for col, (key, value) in enumerate([
                ('教师姓名', teacher['教师姓名']),
                ('综合得分', teacher['综合得分']),
                ('评分人数', teacher['评分人数']),
                ('教学', teacher['教学']),
                ('给分', teacher['给分']),
                ('推荐', teacher['推荐']),
                ('总评分', teacher['总评分']),
                ('备注', teacher['备注'])
            ]):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
        
        # 更新推荐说明
        best_teacher = recommendations[0]
        recommendation_text = (
            f"推荐教师: {best_teacher['教师姓名']}\n"
            f"综合得分: {best_teacher['综合得分']}\n"
            f"优势: "
        )
        
        advantages = []
        if best_teacher['教学'] >= 85:
            advantages.append("教学评分优秀")
        if best_teacher['给分'] >= 85:
            advantages.append("给分较高")
        if best_teacher['推荐'] >= 85:
            advantages.append("学生推荐度高")
        if best_teacher['评分人数'] >= 50:
            advantages.append("样本量充足，评分可信度高")
        
        recommendation_text += "、".join(advantages) if advantages else "暂无特别突出优势"
        self.recommendation_label.setText(recommendation_text) 