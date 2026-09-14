import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import pandas as pd
from scipy.stats import bootstrap, kruskal
import os
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

exp = 'both'
model_kind = ['ori', 'linkGT']
module_name = ['gpt', 'gemini', 'glm', '8b', '40b']
baseline_color = '#F09977'
cot_color = '#9DCD84'


def remove_outliers(data, sigma=3):
    data = np.array(data, dtype=float)
    if len(data) == 0:
        return data
    mean = np.nanmean(data)
    std = np.nanstd(data)
    if std == 0:
        return data
    mask = np.abs(data - mean) <= sigma * std
    filtered = data[mask]
    if len(filtered) == 0:
        return data
    return filtered

def remove_outliers_iqr(data, k=1.5):
    data = np.array(data, dtype=float)
    Q1 = np.nanpercentile(data, 25)
    Q3 = np.nanpercentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - k * IQR
    upper_bound = Q3 + k * IQR
    mask = (data >= lower_bound) & (data <= upper_bound)
    filtered = data[mask]
    return filtered if len(filtered) > 0 else data


def remove_outliers_mad(data, threshold=3.5):
    """
    基于中位数绝对偏差（MAD）过滤异常值
    参数:
        data: 一维 numpy 数组或列表
        threshold: 通常取3或3.5作为判定异常值的阈值
    返回:
        过滤后的数据数组；如果过滤后为空则返回原数据
    """
    data = np.array(data, dtype=float)
    if len(data) <= 1:
        return data

    median = np.nanmedian(data)
    mad = np.nanmedian(np.abs(data - median))
    if mad == 0:
        return data

    # 计算 modified Z-score
    # 通常系数0.6745是为了使MAD在正态分布下与标准差相匹配
    modified_z_scores = 0.6745 * (data - median) / mad

    # 过滤
    mask = np.abs(modified_z_scores) <= threshold
    filtered = data[mask]
    # 若过滤后为空，则返回原数据以避免后续计算出错
    return filtered if len(filtered) > 0 else data

def log2_error(judged_percent):
    return np.log2(np.abs(judged_percent) * 0.1 + 1 / 8)

def load_data1():
    confidence_intervals = {}
    model_error_list = {}
    frequency_rows = {
        1: (0, 5), 3: (6, 11), 5: (12, 17),
        7: (18, 23), 9: (24, 29)
    }
    for mk in model_kind:
        confidence_intervals[mk] = {}
        model_error_list[mk] = {}
        for model in module_name:
            confidence_intervals[mk][model] = (0, 0)
            model_error_list[mk][model] = []

    for mk in model_kind:
        for model in module_name:
            filename = f"{model}_{mk}.xlsx"
            excel_path = os.path.join('result_excel/exp1_linking', filename)
            if not os.path.exists(excel_path):
                continue

            df = pd.read_excel(excel_path, sheet_name=None, header=0)
            error_values = []
            for cmap_name, data in df.items():
                for freq, (start, end) in frequency_rows.items():
                    data_block = data.iloc[start:end + 1, 1:].values
                    if data_block.size == 0:
                        continue

                    row_means = []
                    for row in data_block:
                        filtered_row = remove_outliers(row, sigma=3)
                        # filtered_row = remove_outliers_iqr(row, k=1.5)
                        # filtered_row = remove_outliers_mad(row, threshold=3.5)
                        row_mean = np.nanmean(filtered_row)
                        row_means.append(row_mean)

                    frequency_mean = np.nanmean(row_means)
                    transformed_error = log2_error(frequency_mean)
                    error_values.append(transformed_error)

                    # error_list = np.nanmean(data_block, axis=0)
                    # mean_error = np.nanmean(error_list, axis=0)
                    # transformed_error = log2_error(mean_error)
                    # error_values.append(transformed_error)

            if len(error_values) == 0:
                confidence_intervals[mk][model] = (0, 0)
                model_error_list[mk][model] = []
            else:
                data_tuple = (error_values,)
                try:
                    res = bootstrap(
                        data_tuple,
                        np.mean,
                        confidence_level=0.95,
                        n_resamples=1000,
                        method='percentile'
                    )
                    ci_lower = res.confidence_interval.low
                    ci_upper = res.confidence_interval.high

                    confidence_intervals[mk][model] = (ci_lower, ci_upper)
                    model_error_list[mk][model] = error_values
                except Exception as e:
                    print(f"Bootstrap 计算失败: {excel_path}, 原因: {e}")
                    confidence_intervals[mk][model] = (0, 0)
                    model_error_list[mk][model] = []

    return model_error_list, confidence_intervals


def plot1(ax, confidence_intervals):
    modules = ['gpt', 'gemini', 'glm', '8b', '40b']
    x_labels = ['GPT-4o', 'Gemini 1.5 Pro', 'GLM-4v-9B', 'InternVL2-8B', 'InternVL2-40B']
    x_positions = np.arange(len(modules))
    mk_offset = {
        'ori': -0.07,
        'linkGT': 0.07
    }
    mk_marker = {
        'ori': 'o',
        'linkGT': '^'
    }

    for mk, model_ci_dict in confidence_intervals.items():
        color = baseline_color if mk == 'ori' else cot_color
        offset_val = mk_offset.get(mk, 0)
        means = []  # Store means to draw lines later
        for i, mod in enumerate(modules):
            if mod not in model_ci_dict:
                continue

            ci_lower, ci_upper = model_ci_dict[mod]
            if ci_lower == 0 and ci_upper == 0:
                continue

            mean = (ci_lower + ci_upper) / 2
            err_lower = mean - ci_lower
            err_upper = ci_upper - mean

            x = i + offset_val

            ax.errorbar(
                x, mean,
                yerr=[[err_lower], [err_upper]],
                fmt=mk_marker.get(mk, 'o'),
                markersize=4,
                capsize=0,
                color=color,
            )
            means.append((x, mean))  # Collect x, mean to draw lines later

            for j in range(len(means) - 1):
                mod1 = modules[j]
                mod2 = modules[j + 1]

                # 跳过 Gemini 和 InternVL2-8B 之间的连线
                if mod1 == 'gemini' and mod2 == 'glm':
                    continue

                x1, y1 = means[j]
                x2, y2 = means[j + 1]
                ax.plot([x1, x2], [y1, y2], color='lightgray', linewidth=1)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Models")
    ax.set_ylabel("Log Error")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis="y", alpha=0.5)


def load_data2():
    confidence_intervals = {}
    model_acc_list = {}
    for mk in model_kind:
        confidence_intervals[mk] = {}
        model_acc_list[mk] = {}
        for model in module_name:
            confidence_intervals[mk][model] = (0, 0)
            model_acc_list[mk][model] = []

    colormaps = ['extbodyheat', 'greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'coolwarm', 'rainbow',
                 'spectral', 'blueyellow']
    for mk in model_kind:
        for model in module_name:
            filename = f"{model}_{mk}.xlsx"
            excel_path = os.path.join('result_excel/exp2_linking', filename)
            if not os.path.exists(excel_path):
                continue

            try:
                print(filename)
                file_avg_accuracy_df = pd.read_excel(excel_path, sheet_name='File_Avg_Accuracy')
            except Exception as e:
                print(f"读取文件失败: {excel_path}, 原因: {e}")
                continue

            acc_values = []
            for cmap in colormaps:
                cmap_data = file_avg_accuracy_df[file_avg_accuracy_df['File'].str.contains(cmap)]
                mean_accuracy = cmap_data['Average Accuracy'].mean()
                error_rate = 100 - mean_accuracy
                acc_values.append(error_rate)

            if len(acc_values) == 0:
                confidence_intervals[mk][model] = (0, 0)
                model_acc_list[mk][model] = []
            else:
                data_tuple = (acc_values,)
                try:
                    res = bootstrap(
                        data_tuple,
                        np.mean,
                        confidence_level=0.95,
                        n_resamples=1000,
                        method='percentile'
                    )
                    ci_lower = res.confidence_interval.low
                    ci_upper = res.confidence_interval.high
                    confidence_intervals[mk][model] = (ci_lower, ci_upper)
                    model_acc_list[mk][model] = acc_values
                except Exception as e:
                    print(f"Bootstrap 计算失败: {excel_path}, 原因: {e}")
                    confidence_intervals[mk][model] = (0, 0)
                    model_acc_list[mk][model] = []

    return model_acc_list, confidence_intervals


def plot2(ax, confidence_intervals):
    modules = ['gpt', 'gemini', 'glm', '8b', '40b']
    x_labels = ['GPT-4o', 'Gemini 1.5 Pro', 'GLM-4v-9B', 'InternVL2-8B', 'InternVL2-40B']
    x_positions = np.arange(len(modules))

    mk_offset = {
        'ori': -0.07,
        'linkGT': 0.07
    }
    mk_marker = {
        'ori': 'o',
        'linkGT': '^'
    }

    legend_labels = set()

    for mk, model_ci_dict in confidence_intervals.items():
        color = baseline_color if mk == 'ori' else cot_color
        offset_val = mk_offset.get(mk, 0)
        means = []  # Store means to draw lines later
        for i, mod in enumerate(modules):
            if mod not in model_ci_dict:
                continue
            ci_lower, ci_upper = model_ci_dict[mod]
            if ci_lower == 0 and ci_upper == 0:
                continue
            mean = (ci_lower + ci_upper) / 2
            err_lower = mean - ci_lower
            err_upper = ci_upper - mean
            x = i + offset_val

            label = f"{mk}" if f"{mk}" not in legend_labels else None
            if label is not None:
                legend_labels.add(f"{mk}")

            ax.errorbar(
                x, mean,
                yerr=[[err_lower], [err_upper]],
                fmt=mk_marker.get(mk, 'o'),
                markersize=4,
                capsize=0,
                color=color,
                label=label
            )
            means.append((x, mean))  # Collect x, mean to draw lines later

        # Draw lines between the points
        if means:
            x_vals, y_vals = zip(*means)  # Unzip the collected x, y points
            ax.plot(x_vals, y_vals, color='lightgray', linewidth=1)  # Draw the line

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Models")
    ax.set_ylabel("Error rate")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis="y", alpha=0.5)

if __name__ == "__main__":
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # 加载 exp1 数据，并绘制左侧图（Log Error 图）
    model_error_list1, confidence_intervals1 = load_data1()
    print("exp1 confidence_intervals:")
    print(confidence_intervals1)
    plot1(axs[0], confidence_intervals1)

    # 加载 exp2 数据，并绘制右侧图（Accuracy 图）
    model_acc_list2, confidence_intervals2 = load_data2()
    print("exp2 confidence_intervals:")
    print(confidence_intervals2)
    plot2(axs[1], confidence_intervals2)
    legend_elements = [
        Line2D([0], [0], color=baseline_color, marker='o', linestyle='None',
               markersize=6, markeredgewidth=0, label='Original',
               markerfacecolor=baseline_color),
        Line2D([0], [0], color=cot_color, marker='^', linestyle='None',
               markersize=6, markeredgewidth=0, label='Fine-tuned',
               markerfacecolor=cot_color)
    ]

    # 添加图例到顶部
    fig.legend(
        handles=legend_elements,
        loc='upper center',
        ncol=2,
        bbox_to_anchor=(0.5, 1.08),
        frameon=False,
        fontsize=12
    )
    plt.tight_layout()
    plt.savefig('section5-2-2single.png', dpi=300, bbox_inches='tight')
    plt.savefig('section5-2-2single.pdf', dpi=300, bbox_inches='tight', format='pdf')
    plt.show()
