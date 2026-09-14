import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportion_confint

# 读取Excel文件中的特定Sheet
df = pd.read_excel(r'F:\submit data\experiment result\task2\ori\CoT\8b_ori_cot.xlsx', sheet_name='File_Level_Accuracy')

# 从File字段提取Frequency（比如f1, f2, ..., f5）
df['Frequency'] = df['File'].str.extract(r'(f\d)')

# 把Correct列统一为布尔类型
df['Correct'] = df['Correct'].astype(bool)

# 按 Frequency 和 Colormap 分组
grouped = df.groupby(['Frequency', 'Colormap'])

# 计算准确率和置信区间
results = []
for (freq, cmap), group in grouped:
    n_total = len(group)
    n_correct = group['Correct'].sum()
    accuracy = n_correct / n_total

    # Wilson置信区间 (95%)
    ci_low, ci_upp = proportion_confint(count=n_correct, nobs=n_total, method='wilson')

    results.append({
        'Frequency': freq,
        'Colormap': cmap,
        'Accuracy': accuracy,
        '95% CI Lower': ci_low,
        '95% CI Upper': ci_upp
    })

# 转成DataFrame
results_df = pd.DataFrame(results)

# 显示结果
print(results_df)

# 如果想保存成Excel可以加一句
# results_df.to_excel('/mnt/data/output_accuracy_results.xlsx', index=False)
