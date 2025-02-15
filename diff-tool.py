import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import xml.etree.ElementTree as ET

# 全局变量来保存选择的文件路径
file1_path = None
file2_path = None

def open_file_dialog(title="选择文件"):
    """弹出文件选择对话框，返回选择的文件路径"""
    return filedialog.askopenfilename(filetypes=[("Buffer files", "*.iv"),
                                                ("All files", "*.*")],
                                       title=title)

def select_file1():
    """选择原始文件"""
    global file1_path
    file1_path = open_file_dialog("选择原始文件")
    if file1_path:
        # 更新标签显示文件名
        file1_label.config(text=f"原始文件: {file1_path.split('/')[-1]}")
        print(f"选择的原始文件：{file1_path}")  # Debug: 打印文件路径

def select_file2():
    """选择对比文件"""
    global file2_path
    file2_path = open_file_dialog("选择对比文件")
    if file2_path:
        # 更新标签显示文件名
        file2_label.config(text=f"对比文件: {file2_path.split('/')[-1]}")
        print(f"选择的对比文件：{file2_path}")  # Debug: 打印文件路径

def parse_xml(file_path):
    """解析 XML 文件，返回一个字典：{Path: InitialValue}"""
    tree = ET.parse(file_path)
    root = tree.getroot()

    data_dict = {}
    for variable in root.findall(".//Variable"):
        path = variable.get('Path')
        initial_value = variable.get('InitialValue')
        if path and initial_value:
            data_dict[path.strip()] = initial_value.strip()

    return data_dict

def float_equals(value1, value2, epsilon):
    """判断两个浮点数是否相等，考虑误差范围"""
    try:
        return abs(float(value1) - float(value2)) < epsilon
    except ValueError:
        # 如果不能转换为浮点数，认为是非浮点值，直接返回False
        return value1 == value2

def show_diff():
    """显示两个文件的差异"""
    if not file1_path or not file2_path:
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "请先选择两个文件进行对比。\n")
        return

    try:
        # 解析 XML 文件
        file1_dict = parse_xml(file1_path)
        file2_dict = parse_xml(file2_path)

        print(f"读取到原始文件的变量数：{len(file1_dict)}")  # Debug: 打印文件1的变量数
        print(f"读取到对比文件的变量数：{len(file2_dict)}")  # Debug: 打印文件2的变量数

    except Exception as e:
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, f"文件读取失败: {e}\n")
        return

    # 获取误差值
    try:
        epsilon = float(epsilon_entry.get()) if epsilon_entry.get() else 0.001
    except ValueError:
        epsilon = 0.001  # 如果输入的不是数字，默认误差值为0.001

    # 清空文本框
    text_box.delete(1.0, tk.END)

    # 配置不同类型的标签（tag）用于显示不同颜色
    text_box.tag_config("changed", foreground="green")  # 变更：绿色
    text_box.tag_config("added", foreground="orange")  # 新增：橙色
    text_box.tag_config("removed", foreground="red")  # 删除：红色

    # 检查文件是否完全相同
    if file1_dict == file2_dict:
        text_box.insert(tk.END, "原始文件和对比文件完全相同。\n")
        return

    # 计算差异并显示
    for path in file1_dict.keys():
        if path in file2_dict:
            # 如果两个文件中都有该路径，检查值是否不同
            if not float_equals(file1_dict[path], file2_dict[path], epsilon):
                text_box.insert(tk.END, f"变更 【{path}】 原始值={file1_dict[path]} | 对比值={file2_dict[path]}\n", 'changed')
        else:
            # 如果原始文件有该路径，但对比文件没有该路径，表示删除
            text_box.insert(tk.END, f"删除 【{path}】 原始值={file1_dict[path]} | 对比值=无\n", 'removed')

    # 检查对比文件中有但原始文件中没有的路径
    for path in file2_dict.keys():
        if path not in file1_dict:
            # 如果对比文件有该路径，但原始文件没有该路径，表示新增
            text_box.insert(tk.END, f"新增 【{path}】 原始值=无 | 对比值={file2_dict[path]}\n", 'added')

# 显示使用说明的弹出窗口
def show_help():
    help_text = """
    使用说明：

    1. 选择原始文件和对比文件：点击"选择原始文件"和"选择对比文件"按钮，分别选择原始文件和对比文件。

    2. 设置浮点数允许差值：在"浮点数允许差值"输入框中输入一个数值，用于比较浮点数时的容忍误差。

    3. 点击"显示文件差异"按钮，软件将显示两个文件的差异，变更项为绿色、新增项为橙色、删除项为红色。

    4. 如果浮点数之间的差异小于指定的允许差值，则认为这两个浮点数相等。

    注意：文件必须为正确的buffer文件格式，且包含path和InitialValue。
    """
    messagebox.showinfo("使用说明", help_text)

# 设置窗口
root = tk.Tk()
root.title("buffer文件对比工具")

# 第一行：原始文件的按钮、标签和使用说明按钮
frame1 = tk.Frame(root)
frame1.pack(padx=5, pady=5, fill="x")

# 设置左侧按钮：选择原始文件
file1_button = tk.Button(frame1, text="选择原始文件", command=select_file1)
file1_button.pack(side="left", padx=2)

# 标签用于显示原始文件的文件名
file1_label = tk.Label(frame1, text="原始文件未选择", anchor="w")
file1_label.pack(side="left", padx=2)

# 设置使用说明按钮
btn_help = tk.Button(frame1, text="使用说明", command=show_help)
btn_help.pack(side="right", padx=2)

# 第二行：对比文件的按钮和标签
frame2 = tk.Frame(root)
frame2.pack(padx=5, pady=5, fill="x")

# 设置左侧按钮：选择对比文件
file2_button = tk.Button(frame2, text="选择对比文件", command=select_file2)
file2_button.pack(side="left", padx=2)

# 标签用于显示对比文件的文件名
file2_label = tk.Label(frame2, text="对比文件未选择", anchor="w")
file2_label.pack(side="left", padx=2)

# 第三行：浮点数允许差值和显示文件差异按钮
frame3 = tk.Frame(root)
frame3.pack(padx=5, pady=5, fill="x")

# 误差值输入框和标签
epsilon_label = tk.Label(frame3, text="浮点数允许差值:")
epsilon_label.pack(side="left", padx=2)

epsilon_entry = tk.Entry(frame3)
epsilon_entry.insert(0, "0.001")  # 设置默认值为 0.001
epsilon_entry.pack(side="left", padx=2)

# 设置显示文件差异按钮
btn_diff = tk.Button(frame3, text="显示文件差异", command=show_diff)
btn_diff.pack(side="right", padx=2)

# 设置文本框，用于显示diff结果
text_box = tk.Text(root, width=100, height=30)
text_box.pack(padx=5, pady=10)

# 运行GUI
root.mainloop()
