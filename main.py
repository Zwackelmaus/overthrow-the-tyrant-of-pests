import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

# === 导入封装模块函数 ===
from picturezz import create_insect_identifier_panel
from brand1 import create_kg_selector  # 调用知识图谱版本的推荐器

# === 配置 ===
ICON_PATH = r"D:\myphd\宠虫\exe1\icon.jpg"

def launch_main_ui():
    root = tk.Tk()
    root.title("Smart Insect Expert System")
    root.geometry("850x600+50+50")
    root.overrideredirect(True)  # 自定义标题栏

    # === 顶部蓝色标题栏 ===
    title_bar = tk.Frame(root, bg="#1E90FF", relief='raised', bd=0, height=30)
    title_bar.pack(fill=tk.X, side=tk.TOP)

    # 图标
    try:
        icon_img = Image.open(ICON_PATH).resize((24, 24), Image.Resampling.LANCZOS)
        icon_img = ImageTk.PhotoImage(icon_img)
        icon_label = tk.Label(title_bar, image=icon_img, bg="#1E90FF")
        icon_label.image = icon_img
        icon_label.pack(side=tk.LEFT, padx=5)
    except Exception:
        icon_label = tk.Label(title_bar, text="🐞", bg="#1E90FF", font=("Arial", 12))
        icon_label.pack(side=tk.LEFT, padx=5)

    # 拖动窗口功能
    def start_move(event):
        root.x = event.x
        root.y = event.y
    def do_move(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        root.geometry(f"+{root.winfo_x() + deltax}+{root.winfo_y() + deltay}")

    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)

    # 控制按钮
    btn_frame = tk.Frame(title_bar, bg="#1E90FF")
    btn_frame.pack(side=tk.RIGHT)

    tk.Button(btn_frame, text="_", command=root.iconify, bg="#1E90FF", fg="white", bd=0).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="◻", command=lambda: root.state('zoomed' if root.state() != 'zoomed' else 'normal'), bg="#1E90FF", fg="white", bd=0).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="✖", command=root.destroy, bg="#1E90FF", fg="white", bd=0).pack(side=tk.LEFT, padx=5)

    # === 主体区域 ===
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ========== 新加代码：绑定回调 ==========
    import picturezz  # 确保导入

    def on_insect_identified(insect_name):
        print("识别回调，昆虫名:", insect_name)
        # 如果需要联动推荐模块，可在这里写

    picturezz._external_on_insect_identified = on_insect_identified
    # =====================================

    # 上半部分：图像识别面板
    top_frame = tk.LabelFrame(main_frame, text="📸 Insect Identifier", padx=10, pady=10)
    top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    create_insect_identifier_panel(top_frame)

    # 下半部分：知识图谱推荐面板
    bottom_frame = tk.LabelFrame(main_frame, text="🧠 Knowledge Graph: Insecticide & Brand", padx=10, pady=10)
    bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    create_kg_selector(bottom_frame)  # 替换为基于三元组的版本

    root.mainloop()

if __name__ == "__main__":
    launch_main_ui()
