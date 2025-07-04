# 北京大学智能选课系统

一个基于PyQt5开发的智能选课系统，专为北京大学计算机相关专业设计，集成了AI智能评估功能。

## ✨ 主要功能

- **智能选课流程**：根据年级和专业自动推荐相关课程
- **AI智能评估**：使用DeepSeek AI分析选课合理性并提供建议
- **教师推荐**：为必修课程推荐优秀教师
- **实时学分统计**：动态显示已选学分和课程信息
- **现代化界面**：美观的UI设计，支持动画效果

## 🎯 支持的专业

- 电子信息与技术
- 信息与计算科学  
- 智能科学与技术
- 应用物理学
- 计算机科学与技术
- 通班

## 演示视频
https://disk.pku.edu.cn/link/AAEEC494BFBEAD47359F7BCFFE1957ED69
文件名：程设最终视频.mp4
有效期限：2025-07-29 23:22
提取码：oTBi

## 🚀 快速开始

### 环境要求
- Python 3.7+
- Windows 10/11

### 一键启动
```bash
# 方式1：双击运行（推荐）
run.bat

# 方式2：Python启动
python start_system.py
```

### 安装依赖
```bash
pip install -r requirements.txt
```

## 📖 使用流程

1. **启动系统** → 点击"开始选课"
2. **选择年级** → 大一到大四
3. **选择专业** → 计算机相关专业
4. **选择必修课** → 根据专业自动加载
5. **选择选修课** → 选择性必修和通识课程
6. **教师推荐** → 查看推荐教师
7. **AI评估** → 获得智能分析和建议
8. **查看课表** → 最终选课结果

## 🛠️ 项目结构

```
├── start_system.py          # 系统启动脚本
├── main_enhanced.py         # 主程序
├── config.py               # 配置文件
├── llm_integration.py      # AI集成模块
├── welcome.py              # 欢迎界面
├── age.py                  # 年级选择
├── major.py                # 专业选择
├── compulsory_choose.py    # 必修课选择
├── optimal_compulsory.py   # 选修课选择
├── optimal.py              # 通识课选择
├── teacher.py              # 教师推荐
├── evaluation.py           # AI评估
├── final.py                # 最终课表
├── res/                    # 资源文件
└── requirements.txt        # 依赖包
```

## 🔧 技术特点

- **PyQt5框架**：稳定可靠的GUI界面
- **AI集成**：DeepSeek大语言模型支持
- **数据驱动**：Excel文件管理课程数据
- **高DPI支持**：适配高分辨率屏幕
- **模块化设计**：清晰的代码结构

## ❓ 常见问题

**Q: 程序无法启动？**
A: 确保已安装Python 3.7+，运行 `pip install -r requirements.txt`

**Q: AI评估不工作？**
A: 检查网络连接，系统会自动使用默认评估

**Q: 界面显示异常？**
A: 确认图片资源文件存在，检查屏幕DPI设置

## 📝 版本信息

- 版本：2.1
- 开发：AI助手 + 用户协作
- 特性：智能选课推荐、AI评估、课程管理

---

💡 **提示**：首次使用建议先运行 `python start_system.py` 进行系统检查 