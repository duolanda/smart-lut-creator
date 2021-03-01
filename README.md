# smart-lut-creator
毕业设计：3D LUT生成与转换软件的研究与开发（Research and Development on Software of Generating and Converting 3D LUT）

针对常见色彩曲线与色彩空间进行色彩技术转换，此外还可进行色彩风格化调整，最终生成标准 3D LUT 文件，兼备 LUT 文件的编辑以及一定的智能化处理。



## 文件列表

### 主要文件

- lut.py - LUT 类，包含输入输出、尺寸修改等针对 LUT 的操作
- GUI.py - Qt GUI，程序启动的入口

### HALD 相关

- generate_HALD.py - 生成 HALD 图片
- lut_compute.py - 通过 HALD 生成对应 LUT

### 功能相关

- lut_IO.py - LUT 的输入输出，目前支持 cube 和 3dl  
- lut_color_enhance.py - 一级校色
- lut_color_space.py - 色彩空间（含色域、Gamma、白点）转换
- auto_wb.py - 自动白平衡
- lut_preview.py - 将 LUT 应用到图像上

### GUI 相关

- Smart LUT Creator.ui - Qt  Designer 生成的可动态加载的图形界面
- icon.png - 程序图标（暂时）
- MyWidget.py - 实现可接受拖拽动作的 myQGraphicsView
- MySignal.py - 帮助 MyWidget 传递信号

### 早期测试用

- lut_generator.py - 测试色彩空间转换 LUT 生成
- lut_editor.py - 测试 LUT 编辑部分

### 其他

- constants.py - 常量定义，来自 lut-maker，未来可能会删除
- kdtree.py - 配合 lut.py 中的 Reverse 方法，未来可能会删除



## 主要参考

- [pylut: Create and Modify 3D LUTs in Python!](https://github.com/gregcotten/pylut)
- [lut-maker: Generate 3D color LUTs in Adobe Cube and Pseudo-3D texture format](https://github.com/faymontage/lut-maker)
- [ColorPy: Physical color calculations in Python.](https://github.com/markkness/ColorPy)
- [pillow-lut-tools: Lookup tables loading, manipulating, and generating for Pillow library](https://github.com/homm/pillow-lut-tools)
- [mahmoudnafifi/WB_sRGB: White balance camera-rendered sRGB images (CVPR 2019)](https://github.com/mahmoudnafifi/WB_sRGB)