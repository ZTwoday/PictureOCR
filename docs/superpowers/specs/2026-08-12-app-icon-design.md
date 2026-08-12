# OCR 截图识字 — 应用图标设计

日期：2026-08-12
状态：待用户审阅

## 1. 目标

给 OCR 截图识字桌面应用加一个应用图标：简笔画风格（黑线、透明底），多尺寸通用（托盘 16px 到快捷方式/exe 256px 都清晰）。

## 2. 视觉设计

### 2.1 图形

四个 L 形角括号框出一个"选区"，中间三行文字（第三行较短，像段落末行）——直接画出"框选截图识字"这个动作。

```
┌─┐
│  ──────
│  ──────
│  ────
└─┘
```

含义：取景框 = 框选；文字行 = 识别的文字。

### 2.2 风格参数（viewBox 0 0 64 64）

| 元素 | 参数 |
|---|---|
| 角括号 | L 形，stroke 4.5，圆头 |
| 文字行 | 三行，stroke 4，圆头 |
| 颜色 | 黑色 `#111`，透明底 |
| 角括号实/虚线 | 默认**实线**（虚线为备选，改一处即可） |

几何坐标（可在 SVG 中手改）：

- 角括号：`M17 10 H10 V17` / `M47 10 H54 V17` / `M10 47 V54 H17` / `M54 47 V54 H47`
- 文字行：`M22 28 H42` / `M22 38 H42` / `M22 48 H34`

### 2.3 托盘版

同款图形、白色线条（`#fff`），保证 Windows 深色任务栏上可见。这是独立于黑线版的一个小文件。

## 3. 交付文件（`assets/icons/`）

| 文件 | 用途 |
|---|---|
| `app_icon.svg` | 可编辑源文件，唯一几何来源 |
| `app_icon.png` (256px) | 窗口标题栏 / 任务栏 / 全局图标 |
| `app_icon.ico` (16/32/48/64/128/256) | Windows 快捷方式、将来打包 exe 用（交付，不集成进代码） |
| `tray_icon_16.png` / `tray_icon_32.png` (白线) | 系统托盘 |

## 4. 生成方式

写 `scripts/generate_icon.py`：读 `app_icon.svg`，用 PySide6 `QSvgRenderer` 栅格化，输出各尺寸 PNG 与多尺寸 ICO。生成文件提交进仓库，运行时不需要脚本。

若目标环境缺 `PySide6.QtSvg`，退路：脚本用 `QPainter` 直接按 2.2 的几何画图（视觉效果相同），并把该几何同时写出为 `app_icon.svg`。计划中先验证 QtSvg 可用性再定。

## 5. 代码集成

- `main.py::_make_tray_icon`（第 21 行）：改为加载 `tray_icon.png`，不再画蓝色圆角方块。
- 窗口图标：结果浮窗 `ResultPopup`、历史窗口 `HistoryWindow`、设置对话框 `SettingsDialog` 调用 `setWindowIcon(app_icon)`。
- 应用全局：`main()` 中 `app.setWindowIcon(app_icon)`。
- 路径用相对 `main.py` 的绝对路径（`os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons", ...)`），不依赖 CWD。

## 6. 范围之外

- 给 .bat / 快捷方式自动设置图标（用户可手动在快捷方式属性里选 `app_icon.ico`）
- exe 打包与资源嵌入
- 多种主题色
