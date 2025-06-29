import pandas as pd
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, time
import re

@dataclass
class TimeSlot:
    """课程时间槽"""
    day: int  # 1-7 表示周一到周日
    start_slot: int  # 1-12 表示第几节课
    end_slot: int  # 1-12 表示第几节课
    
    def overlaps(self, other: 'TimeSlot') -> bool:
        """检查是否与另一个时间槽重叠"""
        if self.day != other.day:
            return False
        return not (self.end_slot < other.start_slot or self.start_slot > other.end_slot)
    
    @classmethod
    def parse_time_str(cls, time_str: str) -> List['TimeSlot']:
        """解析课程时间字符串
        格式: "周一1-2节,周三3-4节"
        返回: [TimeSlot(1, 1, 2), TimeSlot(3, 3, 4)]
        """
        if not time_str:
            return []
        
        day_map = {
            '周一': 1, '周二': 2, '周三': 3,
            '周四': 4, '周五': 5, '周六': 6, '周日': 7
        }
        
        slots = []
        try:
            time_parts = time_str.split(',')
            for part in time_parts:
                part = part.strip()
                if not part:
                    continue
                
                # 提取星期几
                for day_name, day_num in day_map.items():
                    if day_name in part:
                        # 提取节数
                        slots_str = part.split(day_name)[1].replace('节', '').strip()
                        if '-' in slots_str:
                            start, end = map(int, slots_str.split('-'))
                            slots.append(cls(day_num, start, end))
                        else:
                            slot_num = int(slots_str)
                            slots.append(cls(day_num, slot_num, slot_num))
                        break
            
            return slots
        except Exception as e:
            print(f"解析课程时间出错: {e}")
            return []

@dataclass
class Course:
    """课程信息"""
    name: str
    credit: float
    time: str
    location: str
    teacher: str
    course_type: str
    time_slots: List[TimeSlot] = None
    
    def __post_init__(self):
        """初始化时解析时间槽"""
        self.time_slots = TimeSlot.parse_time_str(self.time)
    
    def conflicts_with(self, other: 'Course') -> bool:
        """检查是否与另一门课程时间冲突"""
        for my_slot in self.time_slots:
            for other_slot in other.time_slots:
                if my_slot.overlaps(other_slot):
                    return True
        return False

class CourseScheduler:
    """课程调度器"""
    
    def __init__(self):
        self.selected_courses: List[Course] = []
        self.available_courses: List[Course] = []
    
    def add_selected_course(self, course: Course):
        """添加已选课程"""
        self.selected_courses.append(course)
    
    def add_available_course(self, course: Course):
        """添加可选课程"""
        self.available_courses.append(course)
    
    def check_conflicts(self, course: Course) -> List[Course]:
        """检查课程与已选课程的冲突
        返回与该课程冲突的已选课程列表
        """
        conflicts = []
        for selected in self.selected_courses:
            if course.conflicts_with(selected):
                conflicts.append(selected)
        return conflicts
    
    def get_available_slots(self) -> Set[Tuple[int, int]]:
        """获取所有可用的时间槽
        返回: {(day, slot), ...} 表示可用的(星期几, 第几节课)组合
        """
        # 所有可能的时间槽
        all_slots = {(day, slot) 
                    for day in range(1, 6)  # 周一到周五
                    for slot in range(1, 13)}  # 第1-12节课
        
        # 移除已被占用的时间槽
        for course in self.selected_courses:
            for time_slot in course.time_slots:
                for slot in range(time_slot.start_slot, time_slot.end_slot + 1):
                    all_slots.discard((time_slot.day, slot))
        
        return all_slots
    
    def recommend_courses(self, 
                        min_credits: float = 0,
                        max_courses: int = None,
                        preferred_days: List[int] = None) -> List[Course]:
        """推荐不冲突的课程
        
        Args:
            min_credits: 最小学分要求
            max_courses: 最多推荐课程数
            preferred_days: 优先推荐的上课日期（1-7表示周一到周日）
        
        Returns:
            推荐的课程列表
        """
        # 获取可用时间槽
        available_slots = self.get_available_slots()
        
        # 对可选课程进行评分
        scored_courses = []
        for course in self.available_courses:
            # 检查是否有时间冲突
            if self.check_conflicts(course):
                continue
            
            # 计算课程评分
            score = 0
            
            # 1. 基础分：课程学分
            score += course.credit * 10
            
            # 2. 时间槽利用率
            course_slots = {(slot.day, s) 
                          for slot in course.time_slots
                          for s in range(slot.start_slot, slot.end_slot + 1)}
            available_course_slots = course_slots & available_slots
            slot_usage = len(available_course_slots) / len(course_slots)
            score += slot_usage * 20
            
            # 3. 优先日期加分
            if preferred_days:
                preferred_slot_count = sum(1 for slot in course.time_slots 
                                        if slot.day in preferred_days)
                score += preferred_slot_count * 5
            
            scored_courses.append((score, course))
        
        # 按评分排序
        scored_courses.sort(reverse=True)
        
        # 选择最佳课程组合
        recommended = []
        current_credits = 0
        
        for _, course in scored_courses:
            # 检查是否达到最大课程数
            if max_courses and len(recommended) >= max_courses:
                break
            
            # 检查是否达到最小学分
            if min_credits and current_credits >= min_credits:
                break
            
            # 添加课程
            recommended.append(course)
            current_credits += course.credit
        
        return recommended
    
    def get_schedule_matrix(self) -> List[List[str]]:
        """生成课程表矩阵
        返回: 12x5的矩阵，表示周一到周五每节课的课程名称
        """
        # 初始化空课表
        schedule = [['' for _ in range(5)] for _ in range(12)]
        
        # 填充课程
        for course in self.selected_courses:
            for time_slot in course.time_slots:
                if 1 <= time_slot.day <= 5:  # 只处理周一到周五
                    for slot in range(time_slot.start_slot - 1, time_slot.end_slot):
                        schedule[slot][time_slot.day - 1] = course.name
        
        return schedule
    
    @staticmethod
    def format_schedule(schedule: List[List[str]]) -> str:
        """格式化课程表为字符串"""
        result = "    周一    周二    周三    周四    周五\n"
        for i, row in enumerate(schedule):
            result += f"{i+1:2d}  "
            for cell in row:
                result += f"{cell:8s}"
            result += "\n"
        return result

def create_course_from_dict(course_dict: Dict) -> Course:
    """从字典创建课程对象"""
    return Course(
        name=course_dict.get('name', '') or course_dict.get('课程名称', ''),
        credit=float(course_dict.get('credit', 0) or course_dict.get('学分', 0)),
        time=course_dict.get('time', '') or course_dict.get('上课时间', ''),
        location=course_dict.get('location', '') or course_dict.get('上课地点', ''),
        teacher=course_dict.get('teacher', '') or course_dict.get('教师', ''),
        course_type=course_dict.get('type', '') or course_dict.get('课程类型', '') or course_dict.get('course_type', '')
    ) 