import tkinter as tk
from tkinter import ttk
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

# ToolTip 工具类
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 20
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="lightyellow", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "9", "normal"))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

# 缩写品牌名
def abbr_label(text):
    words = text.split()
    initials = [w[0].upper() for w in words if w]
    return "".join(initials)

def create_kg_selector(parent_frame,
                       insect_triple_path=r'D:\myphd\宠虫\exe1\insect_triples.csv',
                       brand_triple_path=r'D:\myphd\宠虫\exe1\brand_triples.csv',
                       add_tooltips=False):

    # === 数据读取 ===
    insect_df = pd.read_csv(insect_triple_path)
    brand_df = pd.read_csv(brand_triple_path)

    selected_insect = tk.StringVar()
    selected_drug = tk.StringVar()
    selected_brand = tk.StringVar()

    insects = sorted(insect_df['subject'].dropna().unique().tolist())

    # === 下拉框UI ===
    ttk.Label(parent_frame, text="Select insect:").grid(row=0, column=0, padx=10, pady=10)
    ttk.Label(parent_frame, text="Insecticide:").grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(parent_frame, text="Brand:").grid(row=0, column=2, padx=10, pady=10)

    insect_combo = ttk.Combobox(parent_frame, textvariable=selected_insect, values=insects, state='readonly', width=30)
    insect_combo.grid(row=1, column=0, padx=10, pady=10)

    drug_combo = ttk.Combobox(parent_frame, textvariable=selected_drug, values=[], state='readonly', width=30)
    drug_combo.grid(row=1, column=1, padx=10, pady=10)

    brand_combo = ttk.Combobox(parent_frame, textvariable=selected_brand, values=[], state='readonly', width=30)
    brand_combo.grid(row=1, column=2, padx=10, pady=10)

    # === 作图函数 ===
    def draw_graph(insect=None):
        if not insect:
            return

        G = nx.DiGraph()
        pos = {}

        # 昆虫节点
        G.add_node(insect)
        pos[insect] = (0, 2)

        # 昆虫 → 杀虫剂
        drugs = insect_df[insect_df['subject'] == insect]['object'].dropna().unique().tolist()
        drug_positions = {}
        for i, drug in enumerate(drugs):
            G.add_node(drug)
            G.add_edge(insect, drug, label='is treated by')
            x = i * 2 - (len(drugs) - 1)
            pos[drug] = (x, 1)
            drug_positions[drug] = x

        # 杀虫剂 → 品牌（品牌只显示一次）
        brand_df_unique = brand_df.drop_duplicates(subset=["subject", "object"])
        brand_set = set()
        for drug in drugs:
            brands = brand_df_unique[brand_df_unique["subject"] == drug]["object"].dropna().unique().tolist()
            for j, brand in enumerate(brands):
                if brand not in brand_set:
                    G.add_node(brand)
                    x = drug_positions[drug] + j * 0.6
                    y = 0
                    pos[brand] = (x, y)
                    brand_set.add(brand)
                G.add_edge(drug, brand, label="can be found")

        # 绘图
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        labels = {}
        for node in G.nodes():
            if node in brand_set:
                labels[node] = abbr_label(node)
            else:
                labels[node] = node

        nx.draw_networkx_nodes(G, pos, node_color="white", edgecolors="black", node_size=1800, ax=ax)
        nx.draw_networkx_labels(G, pos, labels, font_color="black", font_size=9, font_family="monospace", ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color="black", ax=ax)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="black", font_size=8, ax=ax)

        fig.tight_layout()
        image_path = os.path.join(os.path.dirname(insect_triple_path), "kg_graph.png")
        fig.savefig(image_path, dpi=300)
        plt.close(fig)

    # === 更新逻辑 ===
    def update_brand(event=None):
        drug = selected_drug.get()
        matching = brand_df[brand_df['subject'] == drug]
        brand_list = matching['object'].dropna().unique().tolist()
        brand_combo['values'] = brand_list
        if brand_list:
            selected_brand.set(brand_list[0])
        else:
            selected_brand.set("")
        draw_graph(selected_insect.get())

    def update_drug(event=None):
        insect = selected_insect.get()
        matching = insect_df[insect_df['subject'] == insect]
        drug_list = matching['object'].dropna().unique().tolist()
        drug_combo['values'] = drug_list
        if drug_list:
            selected_drug.set(drug_list[0])
        else:
            selected_drug.set("")
        update_brand()

    insect_combo.bind("<<ComboboxSelected>>", update_drug)
    drug_combo.bind("<<ComboboxSelected>>", update_brand)

    if add_tooltips:
        ToolTip(insect_combo, "选择昆虫")
        ToolTip(drug_combo, "对应的杀虫剂")
        ToolTip(brand_combo, "对应的品牌")

        # ... 函数末尾，替换原本返回三个变量的地方
    return insect_combo, drug_combo, brand_combo, selected_insect, selected_drug, selected_brand



# 可单独运行调试
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Knowledge Graph Selector")
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)
    create_kg_selector(main_frame)
    root.mainloop()