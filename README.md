# smart-lut-creator
毕业设计：3D LUT生成与转换软件的研究与开发（Research and Development on Software of Generating and Converting 3D LUT）

针对常见色彩曲线与色彩空间进行色彩技术转换，此外还可进行色彩风格化调整，最终生成标准 3D LUT 文件，兼备 LUT 文件的编辑以及一定的智能化处理。



## 文件列表

### 主要文件

- lut.py - LUT 类，包含颜色插值、尺寸修改等针对 LUT 的操作
- GUI.py - Qt GUI，程序启动的入口

### HALD 相关

- generate_HALD.py - 生成 HALD 图片
- lut_compute.py - 通过 HALD 生成对应 LUT

### 功能相关

- lut_IO.py - LUT 的输入输出，目前支持 cube 和 3dl  
- lut_color_enhance.py - 一级校色
- lut_color_space.py - 色彩空间（含色域、Gamma、白点）转换
- auto_wb.py - 自动白平衡
- auto_cb.py - 自动色彩均衡
- lut_preview.py - 将 LUT 应用到图像上

### GUI 相关

- Smart LUT Creator.ui - Qt  Designer 生成的可动态加载的图形界面
- icon.png - 程序图标（暂时）
- hist_dialog.py - 直方图窗口
- output_dialog.py - LUT 导出窗口
- palette_dialog.py - 色卡解析窗口
- my_widget.py - 实现可接受拖拽动作的 myQGraphicsView
- my_signal.py - 帮助 my_widget 传递信号

### 测试

- module_test.py - 所有测试的入口



## 主要参考

- [pylut: Create and Modify 3D LUTs in Python!](https://github.com/gregcotten/pylut)
- [lut-maker: Generate 3D color LUTs in Adobe Cube and Pseudo-3D texture format](https://github.com/faymontage/lut-maker)
- [ColorPy: Physical color calculations in Python.](https://github.com/markkness/ColorPy)
- [pillow-lut-tools: Lookup tables loading, manipulating, and generating for Pillow library](https://github.com/homm/pillow-lut-tools)
- [mahmoudnafifi/WB_sRGB: White balance camera-rendered sRGB images (CVPR 2019)](https://github.com/mahmoudnafifi/WB_sRGB)
- [Simple color balance algorithm using Python 2.7.8 and OpenCV 2.4.10](https://gist.github.com/DavidYKay/9dad6c4ab0d8d7dbf3dc)
- [tzing/tps-deformation: python implementation of thin plate spline function](https://github.com/tzing/tps-deformation)

## 测试环境

- Python 3.6.2
- colorgram.py==1.2.0
- colour-science==0.3.16
- face-recognition==1.3.0
- numpy==1.16.0
- open3d==0.12.0
- opencv-python==3.4.2.16
- Pillow==6.2.2
- pymiere==1.2.1
- PySide6==6.0.0
- qtmodern==0.2.0