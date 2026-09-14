import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# 数据：9个色图，每个色图在5个频率下的正确率（作为subject）
group_data = [
    [0.592105,  0.559211,  0.572368,  0.763158,  0.756579],
    [0.594595,  0.574324,  0.533784,  0.675676,  0.743243],
    [0.573171,  0.640244,  0.646341,  0.756098,  0.841463],
    [0.592105,  0.611842,  0.631579,  0.815789,  0.835526],
    [0.587838,  0.601351,  0.756757,  0.790541,  0.783784],
    [0.493902,  0.670732,  0.792683,  0.810976,  0.865854],
    [0.559211,  0.598684,  0.750000,  0.809211,  0.894737],
    [0.527027,  0.662162,  0.770270,  0.716216,  0.844595],
    [0.628049,  0.652439,  0.768293,  0.804878,  0.932927]
]

ci_data = [
    [[0.513087, 0.671124], [0.479382, 0.639039], [0.492821, 0.651916], [0.694800, 0.831516], [0.687577, 0.825581]],
    [[0.514568, 0.674621], [0.493731, 0.654917], [0.452472, 0.615096], [0.599373, 0.751978], [0.672039, 0.814448]],
    [[0.496671, 0.649670], [0.566016, 0.714472], [0.572396, 0.720287], [0.689679, 0.822516], [0.784973, 0.897954]],
    [[0.513087, 0.671124], [0.533485, 0.690199], [0.554018, 0.709139], [0.753459, 0.878120], [0.775921, 0.895131]],
    [[0.507607, 0.668069], [0.521545, 0.681158], [0.686824, 0.826689], [0.724213, 0.856868], [0.716684, 0.850884]],
    [[0.416576, 0.571229], [0.598047, 0.743416], [0.729984, 0.855382], [0.750420, 0.871531], [0.813143, 0.918565]],
    [[0.479382, 0.639039], [0.519871, 0.677497], [0.680377, 0.819623], [0.746033, 0.872388], [0.845392, 0.944081]],
    [[0.445648, 0.608406], [0.585069, 0.739255], [0.701704, 0.838836], [0.642732, 0.789701], [0.785542, 0.903647]],
    [[0.553295, 0.702802], [0.578788, 0.726090], [0.703036, 0.833549], [0.743585, 0.866171], [0.894238, 0.971616]],
]


# 转置数据，每列代表一个频率点的9个观测值（9个subject）
group_data = np.array(group_data)
group_data = group_data.T  # shape: [5 freq, 9 colormaps]

# 频率标签
frequencies = [3, 5, 7, 9, 11]

# 颜色和标签
colors = ['#919191', '#57b4e9', '#d55e01', '#019e73', '#bd7ddf', '#ce0418', '#ffdb45', '#e79f01', '#5d63e1']
labels = ['greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat', 'coolwarm', 'rainbow', 'spectral',
          'blueyellow']

# 准备画图
fig, ax = plt.subplots(figsize=(6, 4))

# 遍历每条线（每个colormap）
for i in range(group_data.shape[1]):
    # 当前 colormap 的9个观测值在5个频率下的正确率
    values = group_data[:, i] * 100
    # CI数据的上下限，乘以100
    ci_upper, ci_lower = zip(*ci_data[i])  # 获取置信区间的上下限
    ci_lower = np.array(ci_lower) * 100  # 乘以100
    ci_upper = np.array(ci_upper) * 100  # 乘以100

    # 填充置信区间
    ax.fill_between(frequencies, ci_lower, ci_upper, color=colors[i], alpha=0.05)
    # 绘制折线图
    ax.plot(frequencies, values, marker='o', color=colors[i], label=labels[i])

# 设置轴
ax.set_xlabel('Spatial Frequency', fontsize=12)
ax.set_ylabel('Correct (%)', fontsize=12)
ax.set_xticks(frequencies)
ax.set_ylim(0, 105)
ax.set_yticks(range(10, 101, 10))

# 图例与网格
ax.legend(title="Color Map", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.set_facecolor('white')

# 布局
plt.tight_layout()

# 保存
line_chart_path = r'E:\桌面\Final project\drawpic\line\ch_exp2_line.png'
plt.savefig(line_chart_path, dpi=300, bbox_inches='tight')
plt.show()
