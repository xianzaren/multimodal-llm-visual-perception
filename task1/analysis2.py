import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats


# 定义计算 log2 误差的函数
def log2_error(judged_percent):
    return np.log2(np.abs(judged_percent) + 1 / 8)


# 数据
group_data = [
    [0.069492024, 0.150672175, 0.222698042, 0.241894056, 0.302523603],
    [0.053943182, 0.24220554, 0.155397765, 0.306171747, 0.30065476],
    [0.052157919, 0.218015395, 0.319499952, 0.253724638, 0.329743745],
    [0.042417728, 0.079508885, 0.215166015, 0.305930992, 0.352002797],
    [0.027124033, 0.195174818, 0.303639252, 0.231513875, 0.395673336],
    [0.095418888, 0.135830939, 0.193908714, 0.236174133, 0.316382896],
    [0.180755394, 0.020938002, 0.262632874, 0.22517439, 0.352605918],
    [0.129873265, 0.182584919, 0.28397978, 0.206446375, 0.306456794],
    [0.062331808, 0.132546544, 0.323465795, 0.226894167, 0.365965023]
]

# 频率
frequencies = [1, 3, 5, 7, 9]

# 颜色映射
colors = ['#808080', '#87CEEB', '#FF8C00', '#228B22', '#800080', '#FF0000', '#FFFF00', '#000000', '#0000FF']
labels = ['greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat', 'coolwarm', 'rainbow', 'spectral',
          'blueyellow']

# 生成折线图
fig, ax = plt.subplots(figsize=(6, 4))

# 遍历每个数据组
for group, color, label in zip(group_data, colors, labels):
    # 计算log2误差
    values = [abs(log2_error(val * 100)) for val in group]

    # 计算均值
    mean = np.mean(values)

    # 计算标准差
    std_dev = np.std(values, ddof=1)

    # 样本数量
    n = len(values)

    # 计算标准误
    std_error = std_dev / np.sqrt(n)

    # 计算自由度
    df = n - 1

    # 查找95%置信区间的t值
    t_value = stats.t.ppf(1 - 0.025, df)

    # 计算置信区间
    margin_of_error = t_value * std_error
    ci_lower = mean - margin_of_error
    ci_upper = mean + margin_of_error

    # 填充区域，使用置信区间代替固定边界
    ax.fill_between(frequencies, [ci_lower] * len(frequencies), [ci_upper] * len(frequencies), color=color, alpha=0.2)

    # 绘制曲线
    ax.plot(frequencies, values, marker='o', color=color, linestyle='-', label=label, markersize=5)

# 设置轴标签
ax.set_xlabel('Spatial Frequency', fontsize=12)
ax.set_ylabel('Error Rate', fontsize=12)
ax.set_xticks(frequencies)

# 添加图例
ax.legend(title="Color Map", bbox_to_anchor=(1.05, 0.7), loc='upper left', frameon=False)

# 调整背景和网格
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.set_facecolor('white')

# 添加黑色边框
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

# 调整布局
plt.tight_layout()

# 保存折线图
line_chart_path = r'E:\桌面\Final project\drawpic\line\exp1_line.png'
plt.savefig(line_chart_path, dpi=300, bbox_inches='tight')
plt.show()
plt.close()

'''# 计算每组的平均误差
mean_values = [abs(np.mean([(val * 100) for val in group])) for group in group_data]
#std_errors = [np.std([(val * 100) for val in group]) for group in group_data]

# 生成柱状图
fig2, ax2 = plt.subplots(figsize=(6, 4))
x_pos = np.arange(len(labels))
bars = ax2.bar(x_pos, mean_values,  capsize=5, color=colors, alpha=0.9)#yerr=std_errors,

# 设置轴标签和刻度
ax2.set_xlabel('colorscale', fontsize=12)
ax2.set_ylabel('Error Rate', fontsize=12)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(labels, rotation=45, ha="right")

# 调整背景和网格
ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax2.set_facecolor('white')

# 添加黑色边框
for spine in ax2.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

# 调整布局
plt.tight_layout()

# 保存柱状图
bar_chart_path = r'E:\桌面\Final project\drawpic\exp1_bar.png'
plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight')
plt.show()
plt.close()'''

