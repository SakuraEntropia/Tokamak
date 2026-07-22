import taichi as ti
import numpy as np

# --- 1. 环境初始化 ---
ti.init(arch=ti.opengl)

# --- 2. 模拟参数 ---
n_tf, n_pf = 16, 4
n_path_pts, n_tube_pts = 64, 12
n_particles = 5000

# GUI 参数绑定
# params[0]: delta, params[1]: kappa, params[2]: R0 (大半径)
params = ti.field(dtype=float, shape=4)
params[0], params[1], params[2] = 0.4, 1.6, 1.0

# --- 3. 数据场定义 ---
verts_tf = ti.Vector.field(3, dtype=float, shape=(n_tf * n_path_pts * n_tube_pts))
indices_tf = ti.field(int, shape=(n_tf * (n_path_pts - 1) * n_tube_pts * 6))
verts_pf = ti.Vector.field(3, dtype=float, shape=(n_pf * n_path_pts * n_tube_pts))
indices_pf = ti.field(int, shape=(n_pf * (n_path_pts - 1) * n_tube_pts * 6))
pos = ti.Vector.field(3, dtype=float, shape=n_particles)


# --- 4. 核心计算内核 ---
@ti.kernel
def update_mesh_data():
    delta, kappa, R0 = params[0], params[1], params[2]

    # TF 线圈 (D-Shape)
    for i in range(n_tf):
        phi = 2 * np.pi * i / n_tf
        for j in range(n_path_pts):
            t = j / (n_path_pts - 1)
            theta = t * 2 * np.pi
            # 使用 R0 作为大半径基准
            r = R0 + 0.4 * ti.cos(theta + delta * ti.sin(theta))
            z = kappa * 0.4 * ti.sin(theta)
            p1 = ti.Vector([r * ti.cos(phi), r * ti.sin(phi), z])

            normal = ti.Vector([ti.cos(phi), ti.sin(phi), 0.0])
            binormal = ti.Vector([-ti.sin(phi), ti.cos(phi), 0.0])

            for k in range(n_tube_pts):
                angle = k / n_tube_pts * 2 * np.pi
                offset = (ti.cos(angle) * normal + ti.sin(angle) * binormal) * 0.03
                verts_tf[i * n_path_pts * n_tube_pts + j * n_tube_pts + k] = p1 + offset

    # PF 线圈 (Ring)
    for i in range(n_pf):
        z_off = (i - (n_pf - 1) / 2) * 0.5
        radius = R0  # PF 线圈半径跟随大半径调整
        for j in range(n_path_pts):
            t = j / (n_path_pts - 1)
            theta = t * 2 * np.pi
            p1 = ti.Vector([radius * ti.cos(theta), radius * ti.sin(theta), z_off])
            normal = ti.Vector([ti.cos(theta), ti.sin(theta), 0.0])
            binormal = ti.Vector([0.0, 0.0, 1.0])
            for k in range(n_tube_pts):
                angle = k / n_tube_pts * 2 * np.pi
                offset = (ti.cos(angle) * normal + ti.sin(angle) * binormal) * 0.04
                verts_pf[i * n_path_pts * n_tube_pts + j * n_tube_pts + k] = p1 + offset


@ti.kernel
def reset_particles():
    R0 = params[2]
    for i in range(n_particles):
        phi = ti.random() * 2 * np.pi
        r = R0 + (ti.random() - 0.5) * 0.7
        z = (ti.random() - 0.5) * 0.6
        pos[i] = ti.Vector([r * ti.cos(phi), r * ti.sin(phi), z])


@ti.kernel
def update_particles():
    R0 = params[2]
    for i in range(n_particles):
        p = pos[i]
        # 旋转运动 (环向速度)
        vel = ti.Vector([-p.y, p.x, 0.0]).normalized() * 0.02
        pos[i] += vel
        # 动态边界约束：基于当前的 R0
        r_xy = ti.sqrt(p.x ** 2 + p.y ** 2)
        if (r_xy - R0) ** 2 + p.z ** 2 > 0.35 ** 2:
            # 重置到环中心附近
            phi = ti.random() * 2 * np.pi
            pos[i] = ti.Vector([R0 * ti.cos(phi), R0 * ti.sin(phi), 0.0])


# 关键修复：将初始化拆分为两个独立的 Kernel
@ti.kernel
def init_tf_indices():
    for i in range(n_tf):
        for j in range(n_path_pts - 1):
            for k in range(n_tube_pts):
                base = i * n_path_pts * n_tube_pts + j * n_tube_pts
                next_base = base + n_tube_pts
                idx_base = ((i * (n_path_pts - 1) + j) * n_tube_pts + k) * 6
                indices_tf[idx_base + 0] = base + k
                indices_tf[idx_base + 1] = next_base + k
                indices_tf[idx_base + 2] = next_base + (k + 1) % n_tube_pts
                indices_tf[idx_base + 3] = base + k
                indices_tf[idx_base + 4] = next_base + (k + 1) % n_tube_pts
                indices_tf[idx_base + 5] = base + (k + 1) % n_tube_pts


@ti.kernel
def init_pf_indices():
    for i in range(n_pf):
        for j in range(n_path_pts - 1):
            for k in range(n_tube_pts):
                base = i * n_path_pts * n_tube_pts + j * n_tube_pts
                next_base = base + n_tube_pts
                idx_base = ((i * (n_path_pts - 1) + j) * n_tube_pts + k) * 6
                indices_pf[idx_base + 0] = base + k
                indices_pf[idx_base + 1] = next_base + k
                indices_pf[idx_base + 2] = next_base + (k + 1) % n_tube_pts
                indices_pf[idx_base + 3] = base + k
                indices_pf[idx_base + 4] = next_base + (k + 1) % n_tube_pts
                indices_pf[idx_base + 5] = base + (k + 1) % n_tube_pts


# --- 5. 执行 ---
update_mesh_data()
init_tf_indices()
init_pf_indices()
reset_particles()

window = ti.ui.Window("Tokamak Control Center", (1280, 720))
canvas = window.get_canvas()
scene = window.get_scene()
gui = window.get_gui()
camera = ti.ui.Camera()
camera.position(3, 3, 3)
camera.up(0, 0, 1)
camera.lookat(0, 0, 0)

while window.running:
    # 交互式 GUI
    with gui.sub_window("Tokamak Config", 0.05, 0.05, 0.3, 0.3):
        new_delta = gui.slider_float("Triangularity", params[0], 0.0, 1.0)
        new_kappa = gui.slider_float("Elongation", params[1], 1.0, 2.5)
        new_R0 = gui.slider_float("Major Radius", params[2], 0.5, 1.5)

        if new_delta != params[0] or new_kappa != params[1] or new_R0 != params[2]:
            params[0], params[1], params[2] = new_delta, new_kappa, new_R0
            update_mesh_data()

        if gui.button("Reset Particles"):
            reset_particles()

    camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.LMB)
    scene.set_camera(camera)
    scene.point_light(pos=(2, 2, 2), color=(1, 1, 1))

    update_particles()

    scene.mesh(verts_tf, indices_tf, color=(0.9, 0.7, 0.1), two_sided=True)
    scene.mesh(verts_pf, indices_pf, color=(0.2, 0.5, 0.9), two_sided=True)
    scene.particles(pos, radius=0.015, color=(0.2, 0.7, 1.0))

    canvas.scene(scene)
    window.show()