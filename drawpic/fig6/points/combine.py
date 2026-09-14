import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# 创建一些示例数据
data = np.random.rand(10, 10)

# 创建图形和网格布局
fig = plt.figure(figsize=(12, 8))  # 调整尺寸以适应 2 行 4 列布局
gs = GridSpec(2, 5, width_ratios=[2, 1, 1, 1, 1], height_ratios=[1, 1], figure=fig)  # 2 行 5 列布局

# 大图在左侧
ax0 = fig.add_subplot(gs[0, 0])
ax0.imshow(data, cmap='gray')
ax0.set_title('GT')
ax0.axis('off')  # 不显示坐标轴

# 小图在右侧，2行4列
for i in range(8):  # 两行四列的 8 个小图
    row = i // 4  # 计算行数（0 或 1）
    col = i % 4   # 计算列数（0 到 3）
    ax = fig.add_subplot(gs[row, col + 1])  # 放置在右侧
    ax.imshow(data, cmap='gray')
    ax.set_title(f'Model{i+1}')
    ax.axis('off')

# 调整布局，避免标签重叠
plt.tight_layout()

# 显示图像
plt.show()
