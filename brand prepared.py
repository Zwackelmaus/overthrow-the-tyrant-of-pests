# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 10:55:37 2025

@author: 14242
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 10:15:40 2025

@author: 14242
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd

def create_insecticide_selector(parent_frame,
                                 insect_path=r'D:\myphd\宠虫\exe1\虫1.xlsx',
                                 brand_path=r'D:\myphd\宠虫\exe1\brand_output.xlsx'):
    """
    在给定的父窗口中创建昆虫-杀虫剂-品牌选择面板。

    参数:
    - parent_frame: tkinter 的 Frame 或窗口对象
    - insect_path: Excel 路径，含 English Name 和 drug 列
    - brand_path: Excel 路径，含 name 和品牌列
    """

    # 读取数据
    df = pd.read_excel(insect_path)
    brand_df = pd.read_excel(brand_path)

    # 定义变量
    selected_insect = tk.StringVar()
    selected_drug = tk.StringVar()
    selected_brand = tk.StringVar()

    # 提取昆虫列表
    insects = sorted(df['English Name'].dropna().unique().tolist())

    # ===== 标签 =====
    ttk.Label(parent_frame, text="Please choose the little rascal:").grid(row=0, column=0, padx=10, pady=10)
    ttk.Label(parent_frame, text="Available insecticides:").grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(parent_frame, text="Here are the brand recommended:").grid(row=0, column=2, padx=10, pady=10)

    # ===== 下拉菜单 =====
    insect_combo = ttk.Combobox(parent_frame, textvariable=selected_insect, values=insects, state='readonly', width=30)
    insect_combo.grid(row=1, column=0, padx=10, pady=10)

    drug_combo = ttk.Combobox(parent_frame, textvariable=selected_drug, values=[], state='readonly', width=30)
    drug_combo.grid(row=1, column=1, padx=10, pady=10)

    brand_combo = ttk.Combobox(parent_frame, textvariable=selected_brand, values=[], state='readonly', width=30)
    brand_combo.grid(row=1, column=2, padx=10, pady=10)

    # ===== 更新逻辑 =====
    def update_brand_options(event=None):
        drug = selected_drug.get()
        matching_rows = brand_df[brand_df['name'] == drug]

        brand_set = set()
        for _, row in matching_rows.iterrows():
            brands = row[1:].dropna().tolist()
            brand_set.update(brands)

        brand_list = sorted(brand_set)
        brand_combo['values'] = brand_list
        selected_brand.set(brand_list[0] if brand_list else "")

    def update_drug_options(event=None):
        insect = selected_insect.get()
        drug_list = df[df['English Name'] == insect]['drug'].dropna().unique().tolist()
        drug_combo['values'] = drug_list
        selected_drug.set(drug_list[0] if drug_list else "")
        update_brand_options()

    # ===== 绑定事件 =====
    insect_combo.bind("<<ComboboxSelected>>", update_drug_options)
    drug_combo.bind("<<ComboboxSelected>>", update_brand_options)

    # ===== 返回选择变量（可选）=====
    return selected_insect, selected_drug, selected_brand
