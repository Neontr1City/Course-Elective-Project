"""
配置文件 - 管理API密钥和系统配置
"""

import os

# API配置
API_KEYS = {
    # DeepSeek API 密钥 (您提供的密钥)
    'DEEPSEEK_API_KEY': 'sk-ccbf9495384a4d288590f636c7b23a96',
    
    # 其他AI服务的API密钥（如需要可以添加）
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
    'QWEN_API_KEY': os.getenv('QWEN_API_KEY', ''),
    'ZHIPU_API_KEY': os.getenv('ZHIPU_API_KEY', ''),
    'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY', ''),
    
    # 免费API选项（如果有的话）
    'HUGGINGFACE_API_KEY': os.getenv('HUGGINGFACE_API_KEY', ''),
}

# AI服务配置
AI_CONFIG = {
    # 优先使用的AI服务（按顺序尝试）
    'preferred_services': ['deepseek', 'openai', 'zhipu', 'qwen'],
    
    # 默认模型配置
    'default_models': {
        'deepseek': 'deepseek-chat',
        'openai': 'gpt-3.5-turbo',
        'zhipu': 'glm-4',
        'qwen': 'qwen-turbo',
        'huggingface': 'microsoft/DialoGPT-medium'
    },
    
    # API调用参数
    'api_params': {
        'max_tokens': 1500,
        'temperature': 0.7,
        'timeout': 30,
        'retry_times': 2,  # 重试次数
        'retry_delay': 1   # 重试延迟(秒)
    },
    
    # API端点配置
    'api_endpoints': {
        'deepseek': 'https://api.deepseek.com/v1/chat/completions',
        'openai': 'https://api.openai.com/v1/chat/completions',
        'zhipu': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
        'qwen': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
    },
    
    # 备用API端点（如果主要端点不可用）
    'fallback_endpoints': {
        'deepseek_backup': 'https://api.deepseek.com/v1/chat/completions',
        'openai_backup': 'https://api.openai-proxy.com/v1/chat/completions',
        'free_api': 'https://api.chatanywhere.com.cn/v1/chat/completions'
    }
}

# 界面配置
UI_CONFIG = {
    # 动画配置
    'animation': {
        'fade_duration': 500,
        'button_hover_duration': 200,
        'loading_animation_speed': 1000
    },
    
    # 颜色主题
    'colors': {
        'primary': '#2196F3',
        'secondary': '#FF9800',
        'success': '#4CAF50',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'background': '#f0f0f0',
        'text_primary': '#333333',
        'text_secondary': '#666666',
        'border': '#000000',  # 黑色边框
        'white_bg': '#ffffff'  # 白色背景
    },
    
    # 字体配置 - 统一使用楷体
    'fonts': {
        'title': '楷体',
        'content': '楷体',
        'button': '楷体',
        'mono': '楷体',
        'default_size': '12px',
        'title_size': '16px',
        'button_size': '14px'
    },
    
    # 界面样式 - 统一圆角和样式
    'styles': {
        'border_radius': '15px',  # 圆角
        'shadow': '0 2px 10px rgba(0,0,0,0.1)',
        'padding': '15px',
        'margin': '10px',
        'border_width': '2px',  # 边框宽度
        'border_style': 'solid'  # 边框样式
    },
    
    # 统一的组件样式
    'component_styles': {
        'dialog': """
            QDialog {
                background-color: #ffffff;
            }
        """,
        'button': """
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 15px;
                padding: 10px 20px;
                font-family: '楷体';
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
            }
        """,
        'table': """
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 10px;
                font-family: '楷体';
                font-size: 14px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #eeeeee;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                font-family: '楷体';
                font-weight: bold;
                padding: 8px;
            }
        """,
        
        # 学分显示的统一样式
        'credits_display': {
            'background': """
                QPushButton {
                    background-color: #ffffff;
                    border: 2px solid #000000;
                    border-radius: 10px;
                }
            """,
            'label': """
                QLabel {
                    font-family: '楷体';
                    font-size: 18px;
                    font-weight: bold;
                    color: #333333;
                }
            """,
            'lcd': """
                QLCDNumber {
                    background-color: transparent;
                    color: #2196F3;
                    border: none;
                }
            """
        },
        
        'label': """
            QLabel {
                font-family: '楷体';
                font-size: 12px;
                color: #333333;
                background-color: transparent;
            }
        """,
        
        'line_edit': """
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 8px;
                padding: 8px;
                font-family: '楷体';
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """,
        
        'checkbox': """
            QCheckBox {
                font-family: '楷体';
                font-size: 12px;
                color: #333333;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #000000;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: white;
                font-weight: bold;
            }
        """,
        
        'text_browser': """
            QTextBrowser {
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 10px;
                padding: 10px;
                font-family: '楷体';
                font-size: 12px;
            }
        """,
        
        'group_box': """
            QGroupBox {
                font-family: '楷体';
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #000000;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #ffffff;
            }
        """,
    }
}

# 应用程序配置
APP_CONFIG = {
    'name': '北京大学智能选课系统',
    'version': '2.1',
    'window_size': (800, 800),
    'high_dpi_enabled': True,
    'debug_mode': False,
    'auto_save': True,
    'language': 'zh_CN'
}

# 课程配置
COURSE_CONFIG = {
    'default_credit_per_course': 2,
    'max_total_credits': 30,
    'min_compulsory_credits': 10,
    'grade_mapping': {
        "大一": "一上", 
        "大二": "二上", 
        "大三": "三上", 
        "大四": "四上"
    }
}

def get_api_key(service_name: str) -> str:
    """
    获取指定服务的API密钥
    
    Args:
        service_name: 服务名称 (deepseek, openai, qwen, zhipu, claude, huggingface)
        
    Returns:
        API密钥字符串
    """
    key_name = f'{service_name.upper()}_API_KEY'
    return API_KEYS.get(key_name, '')

def is_api_configured(service_name: str) -> bool:
    """
    检查指定服务的API是否已配置
    
    Args:
        service_name: 服务名称
        
    Returns:
        是否已配置
    """
    return bool(get_api_key(service_name))

def get_configured_services() -> list:
    """
    获取已配置的AI服务列表
    
    Returns:
        已配置的服务名称列表
    """
    configured = []
    for service in AI_CONFIG['preferred_services']:
        if is_api_configured(service):
            configured.append(service)
    return configured

def get_fallback_endpoint(service_name: str) -> str:
    """
    获取服务的备用端点
    
    Args:
        service_name: 服务名称
        
    Returns:
        备用端点URL
    """
    fallback_key = f"{service_name}_backup"
    return AI_CONFIG['fallback_endpoints'].get(fallback_key, '')

def update_api_key(service_name: str, api_key: str):
    """
    更新API密钥
    
    Args:
        service_name: 服务名称
        api_key: 新的API密钥
    """
    key_name = f'{service_name.upper()}_API_KEY'
    API_KEYS[key_name] = api_key 