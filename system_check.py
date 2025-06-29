#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import traceback

def check_dependencies():
    """检查依赖项"""
    print("=== 检查依赖项 ===")
    try:
        import PyQt5
        print("✓ PyQt5 导入成功")
    except ImportError as e:
        print(f"✗ PyQt5 导入失败: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas 导入成功")
    except ImportError as e:
        print(f"✗ pandas 导入失败: {e}")
        return False
    
    try:
        import requests
        print("✓ requests 导入成功")
    except ImportError as e:
        print(f"✗ requests 导入失败: {e}")
        return False
    
    return True

def check_files():
    """检查必要文件"""
    print("\n=== 检查必要文件 ===")
    required_files = [
        'main_enhanced.py',
        'compulsory_choose.py',
        'extract_courses.py',
        'config.py',
        'welcome.py',
        'age.py',
        'major.py',
        'optimal.py',
        'optimal_compulsory.py',
        'teacher.py',
        'evaluation.py',
        'final.py',
        'llm_integration.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} 缺失")
            missing_files.append(file)
    
    # 检查资源文件
    res_files = [
        'res/背景.png',
        'res/通班&智能专业课 表格.xlsx',
        'res/北京大学2025春季课表.xlsx'
    ]
    
    for file in res_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} 缺失")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_module_imports():
    """检查模块导入"""
    print("\n=== 检查模块导入 ===")
    modules = [
        'welcome',
        'age',
        'major',
        'compulsory_choose',
        'optimal',
        'optimal_compulsory',
        'teacher',
        'evaluation',
        'final',
        'extract_courses',
        'config',
        'llm_integration'
    ]
    
    failed_imports = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} 导入成功")
        except Exception as e:
            print(f"✗ {module} 导入失败: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def check_ui_classes():
    """检查UI类"""
    print("\n=== 检查UI类 ===")
    ui_checks = [
        ('welcome', 'Ui_Dialog'),
        ('age', 'Ui_Dialog'),
        ('major', 'Ui_Dialog'),
        ('compulsory_choose', 'CompulsoryChooseUi'),
        ('optimal', 'Ui_Dialog'),
        ('optimal_compulsory', 'Ui_Dialog'),
        ('teacher', 'Ui_Dialog'),
        ('evaluation', 'Ui_Dialog'),
        ('final', 'Ui_Dialog')
    ]
    
    failed_checks = []
    for module_name, class_name in ui_checks:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                print(f"✓ {module_name}.{class_name}")
            else:
                print(f"✗ {module_name}.{class_name} 类不存在")
                failed_checks.append(f"{module_name}.{class_name}")
        except Exception as e:
            print(f"✗ {module_name}.{class_name} 检查失败: {e}")
            failed_checks.append(f"{module_name}.{class_name}")
    
    return len(failed_checks) == 0

def check_data_loading():
    """检查数据加载"""
    print("\n=== 检查数据加载 ===")
    try:
        from extract_courses import extract_courses_by_grade_and_major
        
        # 测试课程数据加载
        base_dir = os.path.dirname(os.path.abspath(__file__))
        res_dir = os.path.join(base_dir, "res")
        file_path = os.path.join(res_dir, "北京大学2025春季课表.xlsx")
        
        courses = extract_courses_by_grade_and_major(file_path, "二上", "通班")
        print(f"✓ 课程数据加载成功，找到 {len(courses)} 门课程")
        return True
    except Exception as e:
        print(f"✗ 课程数据加载失败: {e}")
        traceback.print_exc()
        return False

def check_compulsory_ui():
    """检查必修课UI"""
    print("\n=== 检查必修课UI ===")
    try:
        from PyQt5.QtWidgets import QApplication
        from compulsory_choose import CompulsoryChooseUi
        
        # 创建测试应用（如果不存在）
        if not QApplication.instance():
            app = QApplication([])
        
        # 测试创建UI
        dialog = CompulsoryChooseUi(grade="二上", major="通班")
        print("✓ 必修课UI创建成功")
        
        # 测试获取选中课程方法
        selected = dialog.get_selected_courses()
        print("✓ 必修课UI方法调用成功")
        
        return True
    except Exception as e:
        print(f"✗ 必修课UI检查失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主检查函数"""
    print("智能选课系统 - 系统完整性检查")
    print("=" * 50)
    
    checks = [
        ("依赖项检查", check_dependencies),
        ("文件检查", check_files),
        ("模块导入检查", check_module_imports),
        ("UI类检查", check_ui_classes),
        ("数据加载检查", check_data_loading),
        ("必修课UI检查", check_compulsory_ui)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
                print(f"\n{name}: ✓ 通过")
            else:
                print(f"\n{name}: ✗ 失败")
        except Exception as e:
            print(f"\n{name}: ✗ 异常 - {e}")
    
    print("\n" + "=" * 50)
    print(f"检查完成: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 系统检查完全通过！可以正常运行。")
        return True
    else:
        print("⚠️  系统存在问题，请根据上述报告修复。")
        return False

if __name__ == "__main__":
    main() 