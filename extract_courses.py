import pandas as pd
import os
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_time_slot(time_str):
    """解析课程时间格式"""
    if pd.isna(time_str):
        return []
    
    # 处理多种时间格式
    time_slots = []
    time_str = str(time_str)
    
    # 处理类似 "周一3-4节" 的格式
    weekday_map = {'周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5}
    for weekday, num in weekday_map.items():
        if weekday in time_str:
            # 提取节数
            periods = re.findall(r'(\d+)-(\d+)节', time_str)
            if periods:
                start, end = map(int, periods[0])
                time_slots.append((num, start, end))
    
    return time_slots

def has_time_conflict(time1, time2):
    """检查两个课程时间是否冲突"""
    slots1 = parse_time_slot(time1)
    slots2 = parse_time_slot(time2)
    
    for day1, start1, end1 in slots1:
        for day2, start2, end2 in slots2:
            if day1 == day2:  # 同一天
                if not (end1 < start2 or start1 > end2):  # 时间有重叠
                    return True
            return False

def extract_courses_by_grade_and_major(file_path, grade, major, course_type="必修"):
    """
    从Excel文件中提取指定年级和专业的课程信息
    course_type: "必修" 或 "选择性必修"
    """
    try:
        # 获取文件路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        res_dir = os.path.join(base_dir, "res")
        compulsory_file = os.path.join(res_dir, "通班&智能专业课 表格.xlsx")
        
        # 检查文件是否存在
        if not os.path.exists(compulsory_file):
            logger.error(f"必修课程文件不存在: {compulsory_file}")
            raise FileNotFoundError(f"必修课程文件不存在: {compulsory_file}")
        
        if not os.path.exists(file_path):
            logger.error(f"课程详细信息文件不存在: {file_path}")
            raise FileNotFoundError(f"课程详细信息文件不存在: {file_path}")
        
        # 读取Excel文件
        logger.info(f"正在读取必修课程文件: {compulsory_file}")
        compulsory_df = pd.read_excel(compulsory_file)
        logger.info(f"正在读取课程详细信息文件: {file_path}")
        course_df = pd.read_excel(file_path)
        
        # 处理列名中的特殊字符
        compulsory_df.columns = compulsory_df.columns.str.replace('\u200b', '').str.strip()
        course_df.columns = course_df.columns.str.replace('\u200b', '').str.strip()
        
        logger.info(f"通班文件列名: {compulsory_df.columns.tolist()}")
        
        # 检查必要的列是否存在（在清理列名后）
        required_columns = ['课程名称', '选课时间']
        for col in required_columns:
            if col not in compulsory_df.columns:
                logger.error(f"必修课程文件缺少必要的列: {col}")
                logger.error(f"实际列名: {compulsory_df.columns.tolist()}")
                raise ValueError(f"必修课程文件缺少必要的列: {col}")
        
        # 年级映射 - 包含上下半学期和跨学期的课程
        grade_mapping = {
            "大一": ["一上", "一上/下", "一/下", "一下"],
            "大二": ["二上", "二上/下", "二/下", "二下"],
            "大三": ["三上", "三上/下", "三/下", "三下"],
            "大四": ["四上", "四上/下", "四/下", "四下"],
            # 直接学期格式的映射
            "一上": ["一上", "一上/下"],
            "一下": ["一下", "一上/下", "一/下"],
            "二上": ["二上", "二上/下"],
            "二下": ["二下", "二上/下", "二/下"],
            "三上": ["三上", "三上/下"],
            "三下": ["三下", "三上/下", "三/下"],
            "四上": ["四上", "四上/下"],
            "四下": ["四下", "四上/下", "四/下"]
        }
        
        # 获取通班课程
        if major == "通班":
            logger.info(f"处理通班专业课程 - 年级: {grade}, 课程类型: {course_type}")
            # 只根据年级筛选课程
            if grade.endswith('上'):
                grade = f"{grade[0]}下"
            if grade in grade_mapping:
                target_semesters = grade_mapping[grade]
                semester_filter = compulsory_df['选课时间'].isin(target_semesters)
                for semester in target_semesters:
                    semester_filter |= compulsory_df['选课时间'].str.contains(semester, na=False)
                filtered_courses = compulsory_df[semester_filter]
            else:
                logger.warning(f"未识别的年级: {grade}，返回所有课程")
                filtered_courses = compulsory_df

            # 特判“微电子与电路基础”
            if course_type == "选择性必修":
            # 直接在详细课表中查找这两门课
                target_names = ['微电子与电路基础', '人工智能与社会科学']
                courses = []
                for name in target_names:
                    course_info = course_df[course_df['课程名称'] == name]
                    if not course_info.empty:
                        for _, course in course_info.iterrows():
                            course_data = {
                                '课程名称': str(course.get('课程名称', name)),
                                '学分': float(course.get('学分', 0)) if pd.notna(course.get('学分')) else 2,
                                '上课时间': str(course.get('上课时间', '')),
                                '上课地点': str(course.get('上课地点', '')),
                                '教师': str(course.get('教师', '')),
                                '课程容量': int(course.get('课程容量', 0)) if pd.notna(course.get('课程容量')) else 50,
                                '已选人数': int(course.get('已选人数', 0)) if pd.notna(course.get('已选人数', 0)) else 0
                            }
                            courses.append(course_data)
                return courses
        else:
            # 其他专业的处理逻辑保持不变
            logger.info(f"处理{major}专业课程 - {course_type}")
            if '课程类型' in compulsory_df.columns:
                if course_type == "选择性必修":
                    target_courses = compulsory_df[
                        compulsory_df['课程名称'].isin(['微电子与电路基础', '人工智能与社会科学'])
                    ]['课程名称'].tolist()
                else:
                    target_courses = compulsory_df[
                        ~compulsory_df['课程名称'].isin(['微电子与电路基础', '人工智能与社会科学'])
                    ]['课程名称'].tolist()
            else:
                # 如果没有课程类型列，返回前10门课程
                target_courses = compulsory_df.head(10)['课程名称'].tolist()
            logger.info(f"找到{major}{course_type}课程: {len(target_courses)}门")
        
        # 构建课程数据
        courses = []
        for course_name in target_courses:
            # 在北大课表中查找该课程
            if '课程名称' in course_df.columns:
                course_info = course_df[course_df['课程名称'] == course_name]
            else:
                # 如果课表中没有课程名称列，创建基础课程信息
                course_info = pd.DataFrame()
            
            if not course_info.empty:
                for _, course in course_info.iterrows():
                    try:
                        # 获取时间信息，如果为空则生成示例时间
                        course_time = str(course.get('上课时间', '')) if pd.notna(course.get('上课时间')) else ''
                        if not course_time or course_time == 'nan':
                            # 为课程分配示例时间和地点信息
                            days = ['周一', '周二', '周三', '周四', '周五']
                            periods = ['1-2节', '3-4节', '5-6节', '7-8节']
                            locations = ['教学楼A101', '教学楼A102', '教学楼B201', '教学楼B202', '实验楼C301']
                            teachers = ['张教授', '李教授', '王教授', '赵教授', '陈教授', '刘教授']
                            
                            # 生成随机但固定的时间（基于课程名称哈希）
                            course_hash = hash(course_name) % 1000
                            day = days[course_hash % len(days)]
                            period = periods[course_hash % len(periods)]
                            course_time = f'{day}{period}'
                        
                        course_data = {
                            '课程名称': str(course.get('课程名称', course_name)),
                            '学分': float(course.get('学分', 0)) if pd.notna(course.get('学分')) else 2,
                            '上课时间': course_time,
                            '上课地点': str(course.get('上课地点', '')) if pd.notna(course.get('上课地点')) else f'教学楼{hash(course_name) % 5 + 1}01',
                            '教师': str(course.get('教师', '')) if pd.notna(course.get('教师')) else f'教师{hash(course_name) % 6 + 1}',
                            '课程容量': int(course.get('课程容量', 0)) if pd.notna(course.get('课程容量')) else 50,
                            '已选人数': int(course.get('已选人数', 0)) if pd.notna(course.get('已选人数')) else 0
                        }
                        courses.append(course_data)
                    except Exception as e:
                        logger.error(f"处理课程 {course_name} 时出错: {str(e)}")
                        continue
            else:
                # 如果在课表中找不到课程，从必修课表格中获取基础信息
                course_row = compulsory_df[compulsory_df['课程名称'] == course_name]
                if not course_row.empty:
                    course = course_row.iloc[0]
                    try:
                        # 为课程分配示例时间和地点信息
                        import random
                        days = ['周一', '周二', '周三', '周四', '周五']
                        periods = ['1-2节', '3-4节', '5-6节', '7-8节']
                        locations = ['教学楼A101', '教学楼A102', '教学楼B201', '教学楼B202', '实验楼C301']
                        teachers = ['张教授', '李教授', '王教授', '赵教授', '陈教授', '刘教授']
                        
                        # 生成随机但固定的时间（基于课程名称哈希）
                        course_hash = hash(course_name) % 1000
                        day = days[course_hash % len(days)]
                        period = periods[course_hash % len(periods)]
                        location = locations[course_hash % len(locations)]
                        teacher = teachers[course_hash % len(teachers)]
                        
                        course_data = {
                            '课程名称': str(course_name),
                            '学分': float(course.get('学分', 0)) if pd.notna(course.get('学分')) else 2,
                            '上课时间': f'{day}{period}',
                            '上课地点': location,
                            '教师': teacher,
                            '课程容量': 50,
                            '已选人数': 0
                        }
                        courses.append(course_data)
                    except Exception as e:
                        logger.error(f"处理基础课程信息 {course_name} 时出错: {str(e)}")
                        continue
        
        logger.info(f"成功提取{course_type}课程信息: {len(courses)}门课程")
        return courses
        
    except Exception as e:
        logger.error(f"提取课程信息时出错: {str(e)}")
        raise

def get_compulsory_courses(file_path, grade, major):
    """获取必修课程"""
    return extract_courses_by_grade_and_major(file_path, grade, major, "必修")

def get_optional_compulsory_courses(file_path, grade, major):
    """获取选择性必修课程"""
    return extract_courses_by_grade_and_major(file_path, grade, major, "选择性必修")

def get_course_types(file_path):
    """获取所有课程类型"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        res_dir = os.path.join(base_dir, "res")
        compulsory_file = os.path.join(res_dir, "通班&智能专业课 表格.xlsx")
        
        if not os.path.exists(compulsory_file):
            logger.error(f"必修课程文件不存在: {compulsory_file}")
            raise FileNotFoundError(f"必修课程文件不存在: {compulsory_file}")
        
        logger.info(f"正在读取必修课程文件: {compulsory_file}")
        df = pd.read_excel(compulsory_file)
        
        # 对于通班，返回特殊处理
        if "通班" in df['专业'].unique():
            logger.info("返回通班特殊课程类型")
            return ["必修", "选择性必修"]
        
        course_types = sorted(df['课程类型'].unique().tolist())
        logger.info(f"找到课程类型: {course_types}")
        return course_types
    except Exception as e:
        logger.error(f"获取课程类型时出错: {str(e)}")
        raise

def get_majors(file_path):
    """获取所有专业"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        res_dir = os.path.join(base_dir, "res")
        compulsory_file = os.path.join(res_dir, "通班&智能专业课 表格.xlsx")
        
        if not os.path.exists(compulsory_file):
            logger.error(f"必修课程文件不存在: {compulsory_file}")
            raise FileNotFoundError(f"必修课程文件不存在: {compulsory_file}")
        
        logger.info(f"正在读取必修课程文件: {compulsory_file}")
        df = pd.read_excel(compulsory_file)
        
        majors = sorted(df['专业'].unique().tolist())
        logger.info(f"找到专业: {majors}")
        return majors
    except Exception as e:
        logger.error(f"获取专业列表时出错: {str(e)}")
        raise

def get_available_courses(file_path, grade, major):
    """获取可选课程（考虑课程容量）"""
    try:
        courses = extract_courses_by_grade_and_major(file_path, grade, major)
        available_courses = [course for course in courses if course['已选人数'] < course['课程容量']]
        logger.info(f"找到可选课程: {len(available_courses)}门")
        return available_courses
    except Exception as e:
        logger.error(f"获取可选课程时出错: {str(e)}")
        raise

# 获取当前脚本所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))
res_dir = os.path.join(base_dir, "res")
file_path = os.path.join(res_dir, "北京大学2025春季课表.xlsx")

if __name__ == "__main__":
    # 测试代码
    grade = "二上"  # 例如：一上、一下、二上、二下等
    major = "通班"  # 测试通班选课

    try:
        courses = extract_courses_by_grade_and_major(file_path, grade, major)
        print(f"{grade} {major} 的专业课程:")
        for course in courses:
            print(f"- {course['课程名称']} (学分: {course['学分']})")
            print(f"  时间: {course['上课时间']}, 地点: {course['上课地点']}")
            print(f"  教师: {course['教师']}, 容量: {course['课程容量']}, 已选: {course['已选人数']}")
            
            # 测试时间冲突检查
            if course['上课时间']:
                print(f"  时间解析: {parse_time_slot(course['上课时间'])}")
    except Exception as e:
        print(f"错误: {e}")