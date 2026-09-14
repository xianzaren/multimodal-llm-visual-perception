import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Settings
file_path = r'F:\submit data\experiment result\task1\fintuned\8b_baseGT_baseline.xlsx'
labels = ['greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat', 'coolwarm', 'rainbow', 'spectral', 'blueyellow']
colors = ['#919191', '#57b4e9', '#d55e01', '#019e73', '#bd7ddf', '#ce0418', '#ffdb45', '#e79f01', '#5d63e1']
frequencies = [1, 3, 5, 7, 9]

all_results = []

# 2. Read each sheet and process
for label in labels:
    df = pd.read_excel(file_path, sheet_name=label)
    df = df.dropna(how='all').reset_index(drop=True)

    for i in range(5):
        part = df.iloc[i * 5:(i + 1) * 5, :]
        values = part.values.flatten()
        values = values[~np.isnan(values)]

        # Transform data
        transformed_values = np.log2((values * 100) + (1 / 8))

        mean = np.mean(transformed_values)
        std = np.std(transformed_values, ddof=1)
        n = len(transformed_values)

        # 95% confidence interval
        ci_half_width = 1.96 * (std / np.sqrt(n))
        ci_low = mean - ci_half_width
        ci_upp = mean + ci_half_width

        all_results.append({
            'Frequency': f'f{i + 1}',
            'Freq_Num': i + 1,
            'Colormap': label,
            'Mean': mean,
            '95% CI Lower': ci_low,
            '95% CI Upper': ci_upp
        })

# 3. Organize results
results_df = pd.DataFrame(all_results)

# 4. Pivot tables
pivot_mean = results_df.pivot(index='Colormap', columns='Frequency', values='Mean')
pivot_ci_lower = results_df.pivot(index='Colormap', columns='Frequency', values='95% CI Lower')
pivot_ci_upper = results_df.pivot(index='Colormap', columns='Frequency', values='95% CI Upper')

# 5. Save all pivot tables into one Excel file (different sheets)
with pd.ExcelWriter('exp1_all_tables.xlsx') as writer:
    pivot_mean.to_excel(writer, sheet_name='Mean')
    pivot_ci_lower.to_excel(writer, sheet_name='95% CI Lower')
    pivot_ci_upper.to_excel(writer, sheet_name='95% CI Upper')

# 6. Display Mean table as a sample output
pivot_mean
