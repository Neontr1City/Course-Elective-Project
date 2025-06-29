import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from course_scheduler import Course, CourseScheduler
from course_rating import course_rating_manager

@dataclass
class StudentProfile:
    """学生画像"""
    age: str  # 年级
    major: str  # 专业
    interests: List[str]  # 兴趣领域
    preferred_workload: str  # 期望工作量：'low', 'medium', 'high'
    preferred_assessment: str  # 期望考核方式：'exam', 'project', 'mixed'
    preferred_teaching_style: str  # 期望教学风格：'theoretical', 'practical', 'balanced'

class AIRecommender:
    """AI课程推荐器"""
    
    def __init__(self, scheduler: CourseScheduler):
        self.scheduler = scheduler
        self.student_profile = None
    
    def set_student_profile(self, profile: StudentProfile):
        """设置学生画像"""
        self.student_profile = profile
    
    def get_course_features(self, course: Course) -> Dict:
        """获取课程特征"""
        # 获取课程评分信息
        ratings = course_rating_manager.get_course_ratings(course.name)
        
        if not ratings:
            return {
                'workload_score': 0,
                'content_score': 0,
                'assessment_score': 0,
                'teaching_score': 0,
                'review_count': 0
            }
        
        # 计算平均分数
        workload_scores = []
        content_scores = []
        assessment_scores = []
        review_counts = []
        
        for rating in ratings:
            if rating['workload']:
                workload_scores.append(float(rating['workload']))
            if rating['content_score']:
                content_scores.append(float(rating['content_score']))
            if rating['assessment']:
                assessment_scores.append(float(rating['assessment']))
            if rating['review_count']:
                review_counts.append(float(rating['review_count']))
        
        return {
            'workload_score': np.mean(workload_scores) if workload_scores else 0,
            'content_score': np.mean(content_scores) if content_scores else 0,
            'assessment_score': np.mean(assessment_scores) if assessment_scores else 0,
            'review_count': np.mean(review_counts) if review_counts else 0
        }
    
    def calculate_course_score(self, course: Course) -> float:
        """计算课程与学生画像的匹配分数"""
        if not self.student_profile:
            return 0
        
        score = 0
        features = self.get_course_features(course)
        
        # 1. 工作量匹配度 (0-30分)
        workload_score = features['workload_score']
        if self.student_profile.preferred_workload == 'low':
            score += max(0, 30 - workload_score/100 * 30)
        elif self.student_profile.preferred_workload == 'medium':
            score += 30 - abs(50 - workload_score)/100 * 30
        else:  # high
            score += min(30, workload_score/100 * 30)
        
        # 2. 课程内容评分 (0-20分)
        content_score = features['content_score']
        score += content_score/10 * 20
        
        # 3. 评价数量权重 (0-10分)
        review_count = features['review_count']
        score += min(10, review_count/10)
        
        # 4. 时间分布合理性 (0-20分)
        available_slots = self.scheduler.get_available_slots()
        course_slots = {(slot.day, s) 
                       for slot in course.time_slots
                       for s in range(slot.start_slot, slot.end_slot + 1)}
        available_course_slots = course_slots & available_slots
        slot_usage = len(available_course_slots) / len(course_slots)
        score += slot_usage * 20
        
        # 5. 课程类型加权 (0-20分)
        if course.course_type == '通识课':
            # 检查是否匹配学生兴趣
            interest_match = any(interest.lower() in course.name.lower() 
                               for interest in self.student_profile.interests)
            if interest_match:
                score += 20
            else:
                score += 10
        else:
            score += 15  # 必修课和选修课的基础分
        
        return score
    
    def recommend_courses(self, 
                        available_courses: List[Course],
                        top_k: int = 5,
                        min_credits: float = 0) -> List[Dict]:
        """推荐课程
        
        Args:
            available_courses: 可选课程列表
            top_k: 推荐课程数量
            min_credits: 最小学分要求
        
        Returns:
            推荐课程列表，每个元素包含课程信息和推荐理由
        """
        if not self.student_profile:
            return []
        
        # 计算每门课程的得分
        scored_courses = []
        for course in available_courses:
            # 检查是否与已选课程时间冲突
            if self.scheduler.check_conflicts(course):
                continue
            
            score = self.calculate_course_score(course)
            scored_courses.append((score, course))
        
        # 按分数排序
        scored_courses.sort(reverse=True)
        
        # 选择最佳课程组合
        recommended = []
        current_credits = 0
        
        for score, course in scored_courses:
            if len(recommended) >= top_k:
                break
            
            if min_credits and current_credits >= min_credits:
                break
            
            # 生成推荐理由
            features = self.get_course_features(course)
            reasons = []
            
            # 工作量匹配
            workload = features['workload_score']
            if workload < 30:
                workload_desc = "较轻"
            elif workload < 70:
                workload_desc = "适中"
            else:
                workload_desc = "较重"
            
            if self.student_profile.preferred_workload == 'low' and workload < 30:
                reasons.append(f"课程工作量{workload_desc}，符合你的学习节奏")
            elif self.student_profile.preferred_workload == 'medium' and 30 <= workload <= 70:
                reasons.append(f"课程工作量{workload_desc}，适合你的学习计划")
            elif self.student_profile.preferred_workload == 'high' and workload > 70:
                reasons.append(f"课程工作量{workload_desc}，能够充分投入学习")
            
            # 内容评分
            if features['content_score'] >= 8:
                reasons.append("课程内容评分优秀，教学质量有保障")
            elif features['content_score'] >= 7:
                reasons.append("课程内容评分良好，值得选择")
            
            # 时间安排
            available_slots = self.scheduler.get_available_slots()
            course_slots = {(slot.day, s) 
                          for slot in course.time_slots
                          for s in range(slot.start_slot, slot.end_slot + 1)}
            slot_usage = len(course_slots & available_slots) / len(course_slots)
            if slot_usage > 0.8:
                reasons.append("课程时间安排合理，不会与其他课程冲突")
            
            # 兴趣匹配
            if course.course_type == '通识课':
                for interest in self.student_profile.interests:
                    if interest.lower() in course.name.lower():
                        reasons.append(f"课程内容与你的{interest}兴趣相关")
                        break
            
            recommended.append({
                'course': course,
                'score': score,
                'reasons': reasons
            })
            current_credits += course.credit
        
        return recommended
    
    def get_workload_analysis(self, courses: List[Course]) -> Dict:
        """分析课程组合的工作量"""
        if not courses:
            return {
                'total_workload': 'unknown',
                'description': '暂无课程工作量信息',
                'distribution': {}
            }
        
        # 收集每门课的工作量信息
        workloads = []
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'unknown': 0}
        
        for course in courses:
            workload_info = course_rating_manager.get_course_workload_info(course.name)
            level = workload_info['workload']
            distribution[level] += 1
            
            if workload_info.get('score'):
                workloads.append(workload_info['score'])
        
        # 计算总体工作量
        if workloads:
            avg_workload = sum(workloads) / len(workloads)
            if avg_workload >= 80:
                total_level = 'high'
                description = '总体工作量较大，建议合理安排时间'
            elif avg_workload >= 50:
                total_level = 'medium'
                description = '总体工作量适中，比较均衡'
            else:
                total_level = 'low'
                description = '总体工作量较小，可以考虑增加课程'
        else:
            total_level = 'unknown'
            description = '暂无足够的工作量信息进行评估'
        
        return {
            'total_workload': total_level,
            'description': description,
            'distribution': distribution
        } 