# CLAUDE.md — OCR 截图识字应用

## 项目
- Windows 桌面应用：框选屏幕区域 → OCR 识别文字 → 选择复制
- PySide6 GUI + 可插拔 OCR（本地 RapidOCR / 云端百度）

## 约束
- 测试运行前必须设置 QT_QPA_PLATFORM=offscreen（conftest.py 已处理）
- 百度 API 凭据禁止写进代码；存 Windows 凭据管理器
- 数据目录：~/.ocr_app（config.json / history.json / images/）
- venv 在 .venv/，运行：.venv/Scripts/python
