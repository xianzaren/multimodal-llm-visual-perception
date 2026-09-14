import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

# 1. Read the Excel file
df = pd.read_excel(r'F:\submit data\experiment result\task2\finetuned\8b_cotGT_cot.xlsx', sheet_name='File_Level_Accuracy')

# 2. Extract frequency (f1–f5) from the "File" column
df['Frequency'] = df['File'].str.extract(r'(f\d)')

# 3. Convert "Correct" column to boolean
df['Correct'] = df['Correct'].astype(bool)

# 4. Group by Frequency and Colormap
grouped = df.groupby(['Frequency', 'Colormap'])

# 5. Calculate accuracy and Wilson confidence intervals
results = []
for (freq, cmap), group in grouped:
    n_total = len(group)
    n_correct = group['Correct'].sum()
    accuracy = n_correct / n_total
    ci_low, ci_upp = proportion_confint(count=n_correct, nobs=n_total, method='wilson')
    results.append({
        'Frequency': freq,
        'Colormap': cmap,
        'Accuracy (%)': accuracy * 100,             # 这里直接乘以100
        '95% CI Lower (%)': ci_low * 100,            # 同时调整置信区间
        '95% CI Upper (%)': ci_upp * 100
    })

results_df = pd.DataFrame(results)

# 6. Map Frequency to numerical values
freq_mapping = {'f1': 1, 'f2': 3, 'f3': 5, 'f4': 7, 'f5': 9}
results_df['Freq_Num'] = results_df['Frequency'].map(freq_mapping)

# 7. Pivot tables
pivot_acc = results_df.pivot(index='Colormap', columns='Frequency', values='Accuracy (%)')
pivot_ci_lower = results_df.pivot(index='Colormap', columns='Frequency', values='95% CI Lower (%)')
pivot_ci_upper = results_df.pivot(index='Colormap', columns='Frequency', values='95% CI Upper (%)')

# 8. Save all tables into one Excel file (separate sheets)
with pd.ExcelWriter('exp2_all_tables_percent.xlsx') as writer:
    pivot_acc.to_excel(writer, sheet_name='Accuracy (%)')
    pivot_ci_lower.to_excel(writer, sheet_name='95% CI Lower (%)')
    pivot_ci_upper.to_excel(writer, sheet_name='95% CI Upper (%)')

# 9. Plotting (注意绘图时也对应乘100，这里已经是百分比了)
colors = ['#919191', '#57b4e9', '#d55e01', '#019e73', '#bd7ddf', '#ce0418', '#ffdb45', '#e79f01', '#5d63e1']
labels = ['greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat', 'coolwarm', 'rainbow', 'spectral', 'blueyellow']
frequencies = [1, 2, 3, 4, 5]

fig, ax = plt.subplots(figsize=(6, 4))

for color, label in zip(colors, labels):
    cmap = label.lower()
    data = results_df[results_df['Colormap'].str.lower() == cmap].sort_values('Freq_Num')
    acc = data['Accuracy (%)'].values
    ci_lower = data['95% CI Lower (%)'].values
    ci_upper = data['95% CI Upper (%)'].values
    ax.fill_between(frequencies, ci_lower, ci_upper, color=color, alpha=0.05)
    ax.plot(frequencies, acc, marker='o', color=color, linestyle='-', label=label)

ax.set_xlabel('Spatial Frequency', fontsize=12)
ax.set_ylabel('Correct (%)', fontsize=12)
ax.set_xticks(frequencies)
ax.set_ylim(0, 105)
ax.set_yticks(range(10, 101, 10))
ax.legend(title="Color Map", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.set_facecolor('white')

plt.tight_layout()
line_chart_path = r'exp2_line_percent.png'
plt.savefig(line_chart_path, dpi=300, bbox_inches='tight')
plt.close()