# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 10:26:57 2025

@author: 14242
"""

import os
import pandas as pd
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, scrolledtext

# 设置默认路径
local_root = r"D:\myphd\宠虫\exe1"
model_path = os.path.join(local_root, "efficientnet_b0_finetuned.pth")
data_excel_dir = os.path.join(local_root, "category")
category_image_dir = os.path.join(local_root, "category1")  # 存放识别类别图像的路径

# 模型类名
class_names = [
    'ant', 'bed bug', 'bees', 'beetle', 'caterpillar', 'centipede',
    'cockroach', 'earthworms', 'earwig', 'fly', 'grasshopper', 'leafhopper',
    'mosquito', 'moth', 'silverfish', 'slug', 'snail', 'spider',
    'termite', 'thrips', 'wasp', 'weevil'
]
num_classes = len(class_names)

# 加载模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
model.load_state_dict(torch.load(model_path, map_location=device))
model = model.to(device)
model.eval()

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# 图像识别函数（仅返回类别）
def identify_insect(image_path):
    try:
        image = Image.open(image_path).convert('RGB')
    except:
        return "error", "please upload an image in the correct format"

    input_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_class = class_names[predicted.item()]

    message = f"my name: {predicted_class}"
    # 修改这里，使用csv文件而不是xlsx文件
    csv_file = os.path.join(data_excel_dir, f"{predicted_class}.csv")  # 改后缀为.csv

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)  # 改用read_csv
        accomplices = df.iloc[:, 0].dropna().tolist()
        if accomplices:
            accomplice_str = "\n".join(str(a) for a in accomplices)
            message += f"\nmy accomplice(s) are:\n{accomplice_str}"
        else:
            message += "\nI am the only troublemaker in the family."
    else:
        message += "\nI am the only troublemaker in the family."

    return predicted_class, message

# 主功能封装函数
def create_insect_identifier_panel(parent_frame):
    """
    在父窗口中创建图像识别功能区。
    :param parent_frame: Tkinter Frame 或窗口
    """
    # 主区域分左右两列
    left_frame = tk.Frame(parent_frame)
    left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    right_frame = tk.Frame(parent_frame)
    right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

    # 显示上传和识别图像的区域
    uploaded_img_label = tk.Label(right_frame, text="Uploaded Image")
    uploaded_img_label.pack()
    uploaded_img_canvas = tk.Label(right_frame)
    uploaded_img_canvas.pack(pady=5)

    predicted_img_label = tk.Label(right_frame, text="Predicted Insect Image")
    predicted_img_label.pack()
    btn_show_predicted = tk.Button(right_frame, text="I'm ready to peek at this ichy-wicky picture")
    btn_show_predicted.pack(pady=5)
    predicted_img_canvas = tk.Label(right_frame)
    
    
    def show_predicted_image():
      btn_show_predicted.pack_forget()  # 隐藏按钮
      predicted_img_canvas.pack(pady=5)  # 显示图片

    btn_show_predicted.config(command=show_predicted_image)


    # 上传按钮
    def upload_image():
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        if not filepath:
            return

        # 显示上传图片
        uploaded_image = Image.open(filepath).resize((100, 100))
        uploaded_tk = ImageTk.PhotoImage(uploaded_image)
        uploaded_img_canvas.configure(image=uploaded_tk)
        uploaded_img_canvas.image = uploaded_tk  # 保留引用

        # 执行识别
        predicted_class, result = identify_insect(filepath)
        import picturezz
        if hasattr(picturezz, '_external_on_insect_identified'):
            picturezz._external_on_insect_identified(predicted_class)

        # 显示输出文本
        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, result)

        # 加载类别图像
        predicted_image_path = os.path.join(category_image_dir, f"{predicted_class}.jpg")
        if os.path.exists(predicted_image_path):
            predicted_image = Image.open(predicted_image_path).resize((100, 100))
            predicted_tk = ImageTk.PhotoImage(predicted_image)
            predicted_img_canvas.configure(image=predicted_tk)
            predicted_img_canvas.image = predicted_tk
        else:
            predicted_img_canvas.configure(image='', text="Image not found")

    upload_btn = tk.Button(left_frame, text="Upload Insect Image", command=upload_image,
                           font=("Arial", 12), width=30)
    upload_btn.pack(pady=10)

    # 输出框
    output_box = scrolledtext.ScrolledText(left_frame, height=7, width=50, font=("Courier", 10))
    output_box.pack(padx=10, pady=10)

    # 页脚文字
    footer_text = ("Please look below for the Achilles heel of me and my accomplices.\n"
                   "These arrows may fly, but none will pierce you and your beloved")
    footer_label = tk.Label(left_frame, text=footer_text, font=("Arial", 11), fg="gray")
    footer_label.pack(pady=5)
