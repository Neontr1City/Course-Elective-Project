"""
智能选课系统启动脚本
包含完整的系统检查和启动流程
"""

import sys
import os
import subprocess
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查系统依赖...")
    
    required_packages = [
        'PyQt5',
        'pandas', 
        'openpyxl',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 缺失")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_configuration():
    """检查配置"""
    print("\n🔧 检查系统配置...")
    
    try:
        from config import get_configured_services, APP_CONFIG
        from llm_integration import llm_client
        
        configured_services = get_configured_services()
        
        if configured_services:
            print(f"✅ AI服务配置: {', '.join(configured_services)}")
        else:
            print("⚠️  未配置AI服务，将使用默认评估")
        
        print(f"✅ 应用配置: {APP_CONFIG['name']} v{APP_CONFIG['version']}")
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {str(e)}")
        return False

def check_resources():
    """检查资源文件"""
    print("\n📁 检查资源文件...")
    
    required_files = [
        'res/背景.png',
        'res/剪影.png',
        'res/校名.png',
        'res/通班&智能专业课 表格.xlsx',
        'res/课程评分.xlsx',
    ]
    
    missing_files = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - 文件不存在")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少资源文件: {', '.join(missing_files)}")
        return False
    
    return True

def test_ai_service():
    """测试AI服务连接"""
    print("\n🤖 测试AI服务...")
    
    try:
        from llm_integration import get_ai_evaluation
        from config import get_configured_services
        
        configured_services = get_configured_services()
        
        if not configured_services:
            print("ℹ️  无AI服务配置，将使用默认评估")
            return True
        
        # 简单测试数据
        test_data = {
            "年级": "大二",
            "专业": "计算机科学与技术",
            "必修课程": ["高等数学"],
            "选择性必修": [],
            "通识课程": [],
            "总学分": 5
        }
        
        print(f"🔍 测试 {configured_services[0]} API连接...")
        
        # 快速测试（减少超时时间）
        result = get_ai_evaluation(test_data)
        
        if result and len(result) > 100:
            if "API调用失败" in result or "网络连接失败" in result:
                print("⚠️  AI服务连接异常，将使用默认评估")
            else:
                print("✅ AI服务连接正常")
        else:
            print("⚠️  AI服务响应异常，将使用默认评估")
        
        return True
        
    except Exception as e:
        print(f"⚠️  AI服务测试异常: {str(e)}")
        print("系统将使用默认评估")
        return True

def start_application():
    """启动应用程序"""
    print("\n🚀 启动智能选课系统...")
    print("="*70)
    
    try:
        # 导入并启动主程序
        from main_enhanced import main
        print("✅ 正在启动图形界面...")
        print("\n💡 提示：")
        print("   - 如果界面没有出现，请检查是否有杀毒软件阻止")
        print("   - 可能需要等待几秒钟加载")
        print("   - 关闭此窗口将结束程序")
        print("="*70)
        
        # 启动主程序
        main()
        
    except KeyboardInterrupt:
        print("\n👋 用户取消启动")
    except Exception as e:
        print(f"\n❌ 启动失败: {str(e)}")
        print("\n🔧 故障排除建议:")
        print("1. 确保所有依赖包已正确安装")
        print("2. 检查Python版本是否兼容")
        print("3. 尝试重新安装PyQt5: pip uninstall PyQt5 && pip install PyQt5")
        print("4. 如果问题持续，请运行: python test_config.py")

def show_system_info():
    """显示系统信息"""
    print("="*70)
    print("🎓 北京大学智能选课系统")
    print("="*70)
    print("版本: 2.1")
    print("开发: AI助手 + 用户协作")
    print("特性: 智能选课推荐、AI评估、课程管理")
    print()

def main():
    """主函数"""
    show_system_info()
    
    # 系统检查流程
    checks = [
        ("依赖检查", check_dependencies),
        ("配置检查", check_configuration), 
        ("资源检查", check_resources),
        ("AI服务检查", test_ai_service)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
            print(f"\n❌ {check_name}失败")
            break
        time.sleep(0.5)  # 短暂延迟，让用户看到检查过程
    
    if all_passed:
        print("\n✅ 所有检查通过！")
        time.sleep(1)
        start_application()
    else:
        print(f"\n❌ 系统检查未通过，请解决上述问题后重试")
        print("\n💡 如需帮助，请查看 README.md 文件")
        
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    main() 