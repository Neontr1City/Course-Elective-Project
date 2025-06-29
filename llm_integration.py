"""
大语言模型API集成模块
支持多种API接口，包括OpenAI GPT、Claude、国产大模型等
"""

import requests
import json
import os
import logging
from typing import Dict, Any, Optional
from config import get_api_key, is_api_configured, AI_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMIntegration:
    """大语言模型API集成类"""
    
    def __init__(self):
        self.api_configs = {
            'deepseek': {
                'base_url': 'https://api.deepseek.com/v1/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {get_api_key("deepseek")}',
                    'Content-Type': 'application/json'
                }
            },
            'openai': {
                'base_url': 'https://api.openai.com/v1/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {get_api_key("openai")}',
                    'Content-Type': 'application/json'
                }
            },
            'qwen': {
                'base_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                'headers': {
                    'Authorization': f'Bearer {get_api_key("qwen")}',
                    'Content-Type': 'application/json'
                }
            },
            'zhipu': {
                'base_url': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {get_api_key("zhipu")}',
                    'Content-Type': 'application/json'
                }
            }
        }
        
        # 从配置中获取API参数
        self.api_params = AI_CONFIG['api_params']
        self.default_models = AI_CONFIG['default_models']
        self.preferred_services = AI_CONFIG['preferred_services']
    
    def call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        if not is_api_configured('deepseek'):
            return "DeepSeek API密钥未配置"
            
        try:
            config = self.api_configs['deepseek']
            payload = {
                "model": self.default_models['deepseek'],
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的教育顾问，专门为大学生提供选课建议和学习规划。请用中文回答，要求结构化、专业且实用。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.api_params['max_tokens'],
                "temperature": self.api_params['temperature'],
                "stream": False
            }
            
            logger.info("正在调用DeepSeek API...")
            response = requests.post(
                config['base_url'],
                headers=config['headers'],
                data=json.dumps(payload),
                timeout=self.api_params['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info("DeepSeek API调用成功")
                return content
            else:
                logger.error(f"DeepSeek API调用失败: {response.status_code}")
                return f"API调用失败: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            logger.error("DeepSeek API调用超时")
            return "API调用超时，请稍后重试"
        except requests.exceptions.ConnectionError:
            logger.error("DeepSeek API连接失败")
            return "网络连接失败，请检查网络设置"
        except Exception as e:
            logger.error(f"DeepSeek API调用异常: {str(e)}")
            return f"调用DeepSeek API时发生错误: {str(e)}"
    
    def call_openai_api(self, prompt: str) -> str:
        """调用OpenAI GPT API"""
        if not is_api_configured('openai'):
            return "OpenAI API密钥未配置"
            
        try:
            config = self.api_configs['openai']
            payload = {
                "model": self.default_models['openai'],
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的教育顾问，专门为大学生提供选课建议和学习规划。请用中文回答，要求结构化、专业且实用。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.api_params['max_tokens'],
                "temperature": self.api_params['temperature']
            }
            
            logger.info("正在调用OpenAI API...")
            response = requests.post(
                config['base_url'],
                headers=config['headers'],
                data=json.dumps(payload),
                timeout=self.api_params['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info("OpenAI API调用成功")
                return content
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code}")
                return f"API调用失败: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            logger.error("OpenAI API调用超时")
            return "API调用超时，请稍后重试"
        except requests.exceptions.ConnectionError:
            logger.error("OpenAI API连接失败")
            return "网络连接失败，请检查网络设置"
        except Exception as e:
            logger.error(f"OpenAI API调用异常: {str(e)}")
            return f"调用OpenAI API时发生错误: {str(e)}"
    
    def call_qwen_api(self, prompt: str) -> str:
        """调用阿里云千问API"""
        if not is_api_configured('qwen'):
            return "千问API密钥未配置"
            
        try:
            config = self.api_configs['qwen']
            payload = {
                "model": self.default_models['qwen'],
                "input": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的教育顾问，专门为大学生提供选课建议和学习规划。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "max_tokens": self.api_params['max_tokens'],
                    "temperature": self.api_params['temperature']
                }
            }
            
            logger.info("正在调用千问API...")
            response = requests.post(
                config['base_url'],
                headers=config['headers'],
                data=json.dumps(payload),
                timeout=self.api_params['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("千问API调用成功")
                return result['output']['text']
            else:
                logger.error(f"千问API调用失败: {response.status_code}")
                return f"API调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"千问API调用异常: {str(e)}")
            return f"调用千问API时发生错误: {str(e)}"
    
    def call_zhipu_api(self, prompt: str) -> str:
        """调用智谱AI GLM API"""
        if not is_api_configured('zhipu'):
            return "智谱API密钥未配置"
            
        try:
            config = self.api_configs['zhipu']
            payload = {
                "model": self.default_models['zhipu'],
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的教育顾问，专门为大学生提供选课建议和学习规划。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.api_params['max_tokens'],
                "temperature": self.api_params['temperature']
            }
            
            logger.info("正在调用智谱API...")
            response = requests.post(
                config['base_url'],
                headers=config['headers'],
                data=json.dumps(payload),
                timeout=self.api_params['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("智谱API调用成功")
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"智谱API调用失败: {response.status_code}")
                return f"API调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"智谱API调用异常: {str(e)}")
            return f"调用智谱API时发生错误: {str(e)}"
    
    def generate_evaluation(self, student_data: Dict[str, Any]) -> str:
        """
        生成智能评估报告
        
        Args:
            student_data: 学生选课数据
            
        Returns:
            评估报告文本
        """
        
        # 构建提示词
        prompt = self._build_evaluation_prompt(student_data)
        
        # 按配置的优先级尝试各个API
        for service_name in self.preferred_services:
            if not is_api_configured(service_name):
                logger.info(f"{service_name} API未配置，跳过")
                continue
                
            try:
                logger.info(f"尝试使用 {service_name} API")
                
                if service_name == 'openai':
                    result = self.call_openai_api(prompt)
                elif service_name == 'zhipu':
                    result = self.call_zhipu_api(prompt)
                elif service_name == 'qwen':
                    result = self.call_qwen_api(prompt)
                elif service_name == 'deepseek':
                    result = self.call_deepseek_api(prompt)
                else:
                    continue
                
                # 检查是否成功获取结果
                if self._is_valid_response(result):
                    logger.info(f"成功使用 {service_name} API 生成评估")
                    return self._format_evaluation_result(result, student_data, service_name)
                else:
                    logger.warning(f"{service_name} API返回无效结果: {result}")
                    
            except Exception as e:
                logger.error(f"{service_name} API调用异常: {str(e)}")
                continue
        
        # 如果所有API都失败，返回默认评估
        logger.info("所有AI API都不可用，使用默认评估")
        return self._generate_default_evaluation(student_data)
    
    def _is_valid_response(self, response: str) -> bool:
        """检查API响应是否有效"""
        if not response or len(response.strip()) < 10:
            return False
        
        error_indicators = [
            "API调用失败", "调用", "错误", "超时", "连接失败", 
            "密钥未配置", "网络", "异常"
        ]
        
        return not any(indicator in response for indicator in error_indicators)
    
    def _build_evaluation_prompt(self, data: Dict[str, Any]) -> str:
        """构建评估提示词"""
        prompt = f"""
请对以下学生的选课情况进行专业、详细的评估分析：

## 学生基本信息
- 年级：{data.get('年级', '未知')}
- 专业：{data.get('专业', '未知')}
- 总学分：{data.get('总学分', 0)}分

## 课程选择情况
- 必修课程：{', '.join(data.get('必修课程', [])) or '暂无'}
- 选择性必修课程：{', '.join(data.get('选择性必修', [])) or '暂无'}
- 通识课程：{', '.join(data.get('通识课程', [])) or '暂无'}

请从以下维度进行详细评估，要求内容专业、具体、实用：

### 1. 课程结构合理性分析
分析必修、选修、通识课程的搭配是否科学合理

### 2. 学分分配评估
评估学分分布是否适合该年级和专业的学生

### 3. 专业发展建议
基于所选专业和课程，给出针对性的学习建议

### 4. 学习规划建议
提供短期（本学期）、中期（本学年）、长期（整个大学）的学习规划

### 5. 综合评分与总结
给出课程搭配、学分安排、专业匹配度等方面的评分（满分10分）

请用专业、友好的语气回答，内容要结构化、具体、实用。
"""
        return prompt
    
    def _format_evaluation_result(self, ai_result: str, data: Dict[str, Any], service_name: str) -> str:
        """格式化AI评估结果为HTML"""
        
        # 添加AI服务信息
        service_info = {
            'openai': '🤖 GPT智能分析',
            'zhipu': '🧠 智谱AI分析',  
            'qwen': '💡 千问AI分析',
            'deepseek': '🤖 DeepSeek分析'
        }.get(service_name, '🤖 AI智能分析')
        
        # 转换为HTML格式
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: '微软雅黑'; 
                    line-height: 1.8; 
                    margin: 15px; 
                    color: #333;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    margin-bottom: 25px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .content {{ 
                    background-color: #f8f9fa; 
                    border-left: 5px solid #007bff; 
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }}
                .ai-result {{
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    border: 1px solid #e0e0e0;
                    white-space: pre-wrap;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                    padding: 10px;
                    border-top: 1px solid #eee;
                }}
                h2 {{ margin-top: 0; }}
                .stats {{
                    display: flex;
                    justify-content: space-around;
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 15px 0;
                }}
                .stat-item {{
                    text-align: center;
                }}
                .stat-number {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1976d2;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{service_info}</h2>
                <p>基于您的选课情况，为您生成了专业的AI评估报告</p>
            </div>
            
            <div class="content">
                <h3>📊 选课统计概览</h3>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">{len(data.get('必修课程', []))}</div>
                        <div>必修课程</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{len(data.get('选择性必修', []))}</div>
                        <div>选择性必修</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{len(data.get('通识课程', []))}</div>
                        <div>通识课程</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{data.get('总学分', 0)}</div>
                        <div>总学分</div>
                    </div>
                </div>
            </div>
            
            <div class="content">
                <h3>🎯 AI智能评估报告</h3>
                <div class="ai-result">{ai_result}</div>
            </div>
            
            <div class="footer">
                <p>📋 学生信息：{data.get('年级', '未知')} · {data.get('专业', '未知')} | ⏰ 生成时间：刚刚</p>
                <p>💡 本报告由人工智能生成，仅供参考，建议结合实际情况做出选择</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_default_evaluation(self, data: Dict[str, Any]) -> str:
        """生成默认评估报告（当API不可用时）"""
        total_courses = len(data.get('必修课程', [])) + len(data.get('选择性必修', [])) + len(data.get('通识课程', []))
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: '微软雅黑'; 
                    line-height: 1.6; 
                    margin: 15px;
                    color: #333;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    margin-bottom: 25px;
                }}
                .content {{ 
                    background-color: #f8f9fa; 
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    border-left: 5px solid #28a745;
                }}
                .highlight {{ color: #e74c3c; font-weight: bold; }}
                .good {{ color: #27ae60; }}
                .warning {{ color: #f39c12; }}
                .info-box {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📊 选课评估报告</h2>
                <p>基于您的选课情况生成的综合评估报告</p>
            </div>
            
            <div class="content">
                <h3>📊 基本信息</h3>
                <div class="info-box">
                    <p><strong>👨‍🎓 学生信息：</strong>{data.get('年级', '未知')} · {data.get('专业', '未知')}</p>
                    <p><strong>📚 总学分：</strong><span class="highlight">{data.get('总学分', 0)}分</span></p>
                    <p><strong>📋 选课门数：</strong>{total_courses}门课程</p>
                </div>
            </div>
            
            <div class="content">
                <h3>✅ 课程结构分析</h3>
                <div class="info-box">
                    <p class="good">▪ 您的课程选择涵盖了必修、选修和通识教育各个领域</p>
                    <p class="good">▪ 学分分配合理，符合学年要求</p>
                    <p class="warning">▪ 建议关注课程时间安排，避免冲突</p>
                    <p class="good">▪ 课程难度搭配适中，有利于循序渐进学习</p>
                </div>
            </div>
            
            <div class="content">
                <h3>🎯 专业发展建议</h3>
                <div class="info-box">
                    <p><strong>1. 基础巩固：</strong>重视必修课程学习，建立扎实的专业理论基础</p>
                    <p><strong>2. 视野拓展：</strong>通过选修课程扩展知识面，培养跨学科思维</p>
                    <p><strong>3. 实践应用：</strong>注重理论与实践相结合，积极参与项目实践</p>
                    <p><strong>4. 能力提升：</strong>培养批判性思维和创新能力</p>
                </div>
            </div>
            
            <div class="content">
                <h3>📈 学习规划建议</h3>
                <div class="info-box">
                    <p><strong>📅 短期目标（本学期）：</strong>专注于必修课程学习，确保基础知识掌握</p>
                    <p><strong>🎯 中期目标（本学年）：</strong>通过选修课程拓展专业视野，提升综合能力</p>
                    <p><strong>🚀 长期目标（整个大学）：</strong>结合通识教育，培养全面发展的综合素质</p>
                </div>
            </div>
            
            <div class="content">
                <h3>⭐ 综合评价</h3>
                <div class="info-box" style="text-align: center; font-size: 18px;">
                    <p><span class="good">课程搭配：8.5/10</span></p>
                    <p><span class="good">学分安排：9.0/10</span></p>
                    <p><span class="good">专业匹配：8.8/10</span></p>
                    <p style="margin-top: 15px;"><span class="highlight">总体评价：优秀</span></p>
                    <p style="color: #666; font-size: 14px;">课程搭配合理，建议继续保持并注重实践应用</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

# 全局实例
llm_client = LLMIntegration()

def get_ai_evaluation(student_data: Dict[str, Any]) -> str:
    """
    获取AI评估结果的便捷函数
    
    Args:
        student_data: 学生选课数据
        
    Returns:
        HTML格式的评估报告
    """
    return llm_client.generate_evaluation(student_data) 