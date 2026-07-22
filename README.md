# Tokamak Control Center & Plasma Simulator ⚛️🔥

基于 **Taichi (现代 GGUI 3D 渲染后端)** 开发的托卡马克（Tokamak）磁约束核聚变装置与等离子体粒子流仿真器。本项目通过解析几何与参数化曲线，在 GPU 上实时生成托卡马克核心磁体结构（TF 环向场线圈与 PF 极向场线圈），并动态模拟内部等离子体粒子的环形轨道运动。

---

## 🚀 核心特性

- **磁体参数化动态建模**：
  - **TF 线圈 (Toroidal Field Coils)**：采用经典的 D-Shape（D型截面）设计，引入**三角形变（Triangularity, $\delta$）**与**伸长率（Elongation, $\kappa$）**参数。
  - **PF 线圈 (Poloidal Field Coils)**：多级环形极向场线圈，半径与位置随大半径（$R_0$）自适应。
- **实时 GGUI 交互配置中心**：
  - 支持通过 ImGui 实时调节几何构型：`Triangularity`（三角形变）、`Elongation`（伸长率）与 `Major Radius`（大半径）。
  - 核心网格与边界在参数改变的瞬间自动重新计算并刷新。
- **GPU 高性能等离子体粒子流**：
  - 数千个粒子在托卡马克真空室内做无规则热运动与环向漂移。
  - 动态边界约束：当粒子由于随机游走超出有效磁面边界时，会自动重置回核心区。

---

## 🔬 物理模型与几何方程

托卡马克磁面截面主要通过参数化方程进行演化：
1. **D-Shape 截面生成**：
   - $r = R_0 + a \cdot \cos(	heta + \delta \sin(	heta))$
   - $z = \kappa \cdot a \cdot \sin(	heta)$
   其中 $\delta$ 决定了等离子体的“尖端斜度”（三角形变），$\kappa$ 决定了拉伸程度（伸长率）。
2. **管状网格扫描 (Tube Meshing)**：沿着中心路径外扩 Frenet-Serret标架（法线与仲法线），通过三角面片（Triangles Indices）构建 3D 实体线圈。

---

## 🛠️ 安装与运行指南

确保您的系统已安装支持 OpenGL 后端的 Taichi 以及 Numpy 库。

### 1. 依赖安装
```bash
pip install taichi numpy
```

### 2. 运行脚本
将代码保存为 `tokamak_sim.py` 并运行：
```bash
python tokamak_sim.py
```

---

## 🎛️ 交互控制面板说明

启动程序后，界面左上角将弹出 **Tokamak Config** 控制面板：

- **Tokamak Geometry Config**：
  - `Triangularity`：调节 D-Shape 线圈的顶部尖锐与变形程度。
  - `Elongation`：调节托卡马克的垂直拉伸高度（纵横比/椭圆度）。
  - `Major Radius`：调节整体装置的大半径基准。
- **Action Buttons**：
  - `Reset Particles`：一键重新打散并洗牌等离子体粒子群。
- **Camera Viewport Controls**：
  - 按住鼠标左键拖拽（`LMB`）可自由旋转 3D 视角，观察磁体结构与内部粒子流。

---

## 📜 许可证

本项目基于 MIT License 开源协议。
