import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class CourseRatingManager:
    """课程评分管理器"""
    
    def __init__(self, rating_file_path=None):
        if rating_file_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.rating_file_path = os.path.join(base_dir, "res", "课程评分.xlsx")
        else:
            self.rating_file_path = rating_file_path
        
        self.ratings_data = None
        self.load_ratings()
    
    def load_ratings(self):
        """加载课程评分数据"""
        try:
            if os.path.exists(self.rating_file_path):
                self.ratings_data = pd.read_excel(self.rating_file_path)
                logger.info(f"成功加载课程评分数据，共{len(self.ratings_data)}条记录")
                
                # 清理列名中的特殊字符
                self.ratings_data.columns = [col.strip().replace('\u200b', '') for col in self.ratings_data.columns]
                
                print(f"课程评分数据列名: {self.ratings_data.columns.tolist()}")
                print(f"数据预览:\n{self.ratings_data.head()}")
                
            else:
                logger.warning(f"课程评分文件不存在: {self.rating_file_path}")
                self.ratings_data = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"加载课程评分数据失败: {e}")
            self.ratings_data = pd.DataFrame()
    
    def get_course_ratings(self, course_name):
        """获取指定课程的所有评分信息"""
        if self.ratings_data is None or self.ratings_data.empty:
            return []
        
        try:
            # 查找课程
            course_ratings = self.ratings_data[self.ratings_data['课程'] == course_name]
            
            if course_ratings.empty:
                return []
            
            ratings_list = []
            for _, row in course_ratings.iterrows():
                rating_info = {
                    'teacher': row.get('老师', ''),
                    'content_score': row.get('课程内容 满分10分', 0),
                    'workload': row.get('课程工作量', 0),
                    'assessment': row.get('课程考核', 0),
                    'average_score': row.get('平均分', 0),
                    'review_count': row.get('有效评价条数', 0)
                }
                ratings_list.append(rating_info)
            
            return ratings_list
            
        except Exception as e:
            logger.error(f"获取课程评分失败: {e}")
            return []
    
    def get_teacher_recommendations(self, course_list):
        """根据课程列表获取教师推荐"""
        recommendations = {}
        
        for course_name in course_list:
            ratings = self.get_course_ratings(course_name)
            
            if not ratings:
                recommendations[course_name] = {
                    'status': 'no_data',
                    'message': '暂时没有老师推荐',
                    'recommended_teacher': None
                }
                continue
            
            # 计算每个老师的综合分数
            teacher_scores = {}
            for rating in ratings:
                teacher = rating['teacher']
                if not teacher or pd.isna(teacher):
                    continue
                
                # 综合评分计算：平均分占60%，内容评分占30%，评价数量占10%
                try:
                    avg_score = float(rating['average_score']) if rating['average_score'] else 0
                    content_score = float(rating['content_score']) if rating['content_score'] else 0
                    review_count = float(rating['review_count']) if rating['review_count'] else 0
                    
                    # 标准化评价数量（最多10分）
                    normalized_review_count = min(review_count / 10, 1) * 10
                    
                    comprehensive_score = (avg_score * 0.6 + 
                                         content_score * 0.3 + 
                                         normalized_review_count * 0.1)
                    
                    teacher_scores[teacher] = {
                        'score': comprehensive_score,
                        'avg_score': avg_score,
                        'content_score': content_score,
                        'review_count': review_count,
                        'workload': rating['workload']
                    }
                except (ValueError, TypeError):
                    continue
            
            if teacher_scores:
                # 选择评分最高的老师
                best_teacher = max(teacher_scores.keys(), key=lambda x: teacher_scores[x]['score'])
                best_score_info = teacher_scores[best_teacher]
                
                recommendations[course_name] = {
                    'status': 'success',
                    'recommended_teacher': best_teacher,
                    'score_info': best_score_info,
                    'all_teachers': teacher_scores
                }
            else:
                recommendations[course_name] = {
                    'status': 'no_valid_data',
                    'message': '暂时没有有效的老师评分数据',
                    'recommended_teacher': None
                }
        
        return recommendations
    
    def get_course_workload_info(self, course_name):
        """获取课程工作量信息"""
        ratings = self.get_course_ratings(course_name)
        
        if not ratings:
            return {'workload': 'unknown', 'description': '工作量信息暂无'}
        
        # 计算平均工作量
        workloads = [r['workload'] for r in ratings if r['workload'] and not pd.isna(r['workload'])]
        
        if not workloads:
            return {'workload': 'unknown', 'description': '工作量信息暂无'}
        
        avg_workload = sum(workloads) / len(workloads)
        
        # 工作量等级划分
        if avg_workload >= 80:
            level = 'high'
            description = '工作量较大'
        elif avg_workload >= 50:
            level = 'medium'
            description = '工作量适中'
        else:
            level = 'low'
            description = '工作量较小'
        
        return {
            'workload': level,
            'score': avg_workload,
            'description': description,
            'sample_count': len(workloads)
        }

# 全局实例
course_rating_manager = CourseRatingManager() 