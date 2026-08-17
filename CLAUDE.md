# CLAUDE.md — OCR 截图识字应用

## 项目
- Windows 桌面应用：框选屏幕区域 → OCR 识别文字 → 选择复制
- PySide6 GUI + 可插拔 OCR（本地 RapidOCR / 云端百度）

## 约束
- 测试运行前必须设置 QT_QPA_PLATFORM=offscreen（conftest.py 已处理）
- 百度 API 凭据禁止写进代码；存 Windows 凭据管理器
- 数据目录：~/.ocr_app（config.json / images/）
- venv 在 .venv/，运行：.venv/Scripts/python

## 环境注意事项（重要）
- **PySide6 与 Anaconda ICU 冲突**：Anaconda 的 icuuc.dll 在 PATH 里会被 PySide6 误加载导致 `QtCore` 导入失败（WinError 127）。
  已修复：复制 `C:\Windows\System32\icuuc.dll` 到 `.venv\Lib\site-packages\PySide6\icuuc.dll`。
  **该修复在 venv 外，不随 git 走**——若 venv 被重建或删除，PySide6 任务会全部失败，需重新执行上面的复制命令。
- 不要随意重建 / 重装 .venv，否则上面的 PySide6 修复会丢失。
