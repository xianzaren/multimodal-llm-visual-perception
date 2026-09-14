import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import pandas as pd
from scipy.stats import bootstrap, kruskal
import os

exp = 'both'
prompt_kind = ['baseline', 'cot']
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


def remove_outliers_iqr(data, k=1.5):  # 选用IQR处理结果
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
    return np.log2(np.abs(judged_percent) * 100 + 1 / 8)


def load_data1():
    confidence_intervals = {}
    model_error_list = {}
    frequency_rows = {
        1: (0, 5), 3: (6, 11), 5: (12, 17),
        7: (18, 23), 9: (24, 29)
    }
    mk = 'ori'
    for prompt in prompt_kind:
        confidence_intervals[prompt] = {}
        model_error_list[prompt] = {}
        for model in module_name:
            confidence_intervals[prompt][model] = (0, 0)
            model_error_list[prompt][model] = []

    for prompt in prompt_kind:
        for model in module_name:
            filename = f"{model}_{mk}_{prompt}.xlsx"
            excel_path = os.path.join('result_excel(1)/exp1', filename)
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
                        #filtered_row = remove_outliers(row, sigma=3)
                        filtered_row = remove_outliers_iqr(row, k=1.5)
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
                confidence_intervals[prompt][model] = (0, 0)
                model_error_list[prompt][model] = []
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

                    confidence_intervals[prompt][model] = (ci_lower, ci_upper)
                    model_error_list[prompt][model] = error_values
                except Exception as e:
                    print(f"Bootstrap 计算失败: {excel_path}, 原因: {e}")
                    confidence_intervals[prompt][model] = (0, 0)
                    model_error_list[prompt][model] = []

    return model_error_list, confidence_intervals


def plot1(ax, confidence_intervals):
    modules = ['gpt', 'gemini', 'glm', '8b', '40b']
    # 显示完整的模型名称
    x_labels = ['GPT-4o', 'Gemini 1.5', 'GLM-4v-9B', 'InternVL2-8B', 'InternVL2-40B']
    x_positions = np.arange(len(modules))
    prompt_color = {
        'baseline': baseline_color,
        'cot': cot_color
    }
    mk_marker = {
        'ori': 'o',
        'baseGT': 's',
        'cotGT': '^'
    }
    # mk_offset = {
    #     'ori': -0.15,
    #     'baseGT': 0.0,
    #     'cotGT': 0.15
    # }
    prompt_offset = {
        'baseline': -0.07,
        'cot': 0.07
    }
    mk = 'ori'
    prompt_means = {
        'baseline': [],
        'cot': []
    }
    prompt_gray_color = {
        'baseline': 'lightgray',  # 用不同的灰色调
        'cot': 'darkgray'
    }

    for prompt, model_ci_dict in confidence_intervals.items():
        if not isinstance(model_ci_dict, dict):
            continue

        color = prompt_color.get(prompt, 'gray')
        gray_color = prompt_gray_color.get(prompt, 'gray')
        offset_val = prompt_offset.get(prompt, 0)
        combined_label = f"{prompt}"

        means = []
        for i, mod in enumerate(modules):
            if mod not in model_ci_dict:
                continue

            ci_lower, ci_upper = model_ci_dict[mod]
            if ci_lower == 0 and ci_upper == 0:
                means.append(np.nan)
                continue

            mean = (ci_lower + ci_upper) / 2
            err_lower = mean - ci_lower
            err_upper = ci_upper - mean
            print(mean)
            x = i + offset_val
            means.append(mean)  # Add the mean for the current model to the list

            label = combined_label if i == 0 else None

            ax.errorbar(
                x, mean,
                yerr=[[err_lower], [err_upper]],
                fmt=mk_marker.get(mk, 'o'),
                markersize=6.5,
                capsize=0,
                color=color,
                label=label,
                linewidth=2,
                zorder=3
            )

        prompt_means[prompt] = means
        ax.plot(
            x_positions + prompt_offset.get(prompt, 0),
            means,
            color=gray_color,
            linestyle='-',
            linewidth=1,
            zorder=2
        )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Models")
    ax.set_ylabel("Log Error")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis="y", alpha=0.5)
    # ax.grid(axis="x", alpha=0.3)
    #ax.legend(loc='center')


def load_data2():
    confidence_intervals = {}
    model_acc_list = {}
    mk = 'ori'
    for prompt in prompt_kind:
        confidence_intervals[prompt] = {}
        model_acc_list[prompt] = {}
        for model in module_name:
            confidence_intervals[prompt][model] = (0, 0)
            model_acc_list[prompt][model] = []

    colormaps = ['extbodyheat', 'greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'coolwarm', 'rainbow',
                 'spectral', 'blueyellow']

    for prompt in prompt_kind:
        for model in module_name:
            filename = f"{model}_{mk}_{prompt}.xlsx"
            excel_path = os.path.join('result_excel(1)/exp2', filename)
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
                print(mean_accuracy)
                error_rate = 100 - mean_accuracy
                acc_values.append(error_rate)

            if len(acc_values) == 0:
                confidence_intervals[prompt][model] = (0, 0)
                model_acc_list[prompt][model] = []
            else:
                #acc_values = remove_outliers(acc_values)
                acc_values = remove_outliers_iqr(acc_values)
                #acc_values = remove_outliers_mad(acc_values)
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
                    confidence_intervals[prompt][model] = (ci_lower, ci_upper)
                    model_acc_list[prompt][model] = acc_values
                except Exception as e:
                    print(f"Bootstrap 计算失败: {excel_path}, 原因: {e}")
                    confidence_intervals[prompt][model] = (0, 0)
                    model_acc_list[prompt][model] = []

    return model_acc_list, confidence_intervals


def plot2(ax, confidence_intervals):
    modules = ['gpt', 'gemini', 'glm', '8b', '40b']
    # 显示完整的模型名称
    x_labels = ['GPT-4o', 'Gemini 1.5', 'GLM-4v-9B', 'InternVL2-8B', 'InternVL2-40B']
    x_positions = np.arange(len(modules))

    # 提示类型对应颜色
    prompt_color = {
        'baseline': baseline_color,
        'cot': cot_color
    }
    mk_marker = {
        'ori': 'o',
        'baseGT': 's',
        'cotGT': '^'
    }
    # mk_offset = {
    #     'ori': -0.15,
    #     'baseGT': 0.0,
    #     'cotGT': 0.15
    # }
    prompt_offset = {
        'baseline': -0.05,
        'cot': 0.05
    }

    legend_labels = set()
    prompt_means = {
        'baseline': [],
        'cot': []
    }
    prompt_gray_color = {
        'baseline': 'lightgray',
        'cot': 'darkgray'
    }

    for prompt, model_ci_dict in confidence_intervals.items():
        color = prompt_color.get(prompt, 'gray')
        gray_color = prompt_gray_color.get(prompt, 'gray')
        offset_val = prompt_offset.get(prompt, 0)
        combined_label = f"{prompt}"

        means = []

        for i, mod in enumerate(modules):
            if mod not in model_ci_dict:
                continue
            ci_lower, ci_upper = model_ci_dict[mod]

            if ci_lower == 0 and ci_upper == 0:
                means.append(np.nan)
                continue

            mean = (ci_lower + ci_upper) / 2
            err_lower = mean - ci_lower
            err_upper = ci_upper - mean
            x = i + offset_val
            means.append(mean)

            label = combined_label if combined_label not in legend_labels else None
            if label is not None:
                legend_labels.add(combined_label)

            ax.errorbar(
                x, mean,
                yerr=[[err_lower], [err_upper]],
                fmt=mk_marker.get('ori', 'o'),
                markersize=6.5,
                capsize=0,
                color=color,
                label=label,
                linewidth=2,
                zorder=3
            )

        prompt_means[prompt] = means
        ax.plot(
            x_positions + prompt_offset.get(prompt, 0),
            means,
            color=gray_color,
            linestyle='-',
            linewidth=1,
            zorder=2
        )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Models")
    ax.set_ylabel("Error_rate")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis="y", alpha=0.5)
    #ax.legend()


if __name__ == "__main__":
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # 加载 exp1 数据，并绘制左侧图（Log Error 图）
    model_error_list1, confidence_intervals1 = load_data1()
    print("exp1 confidence_intervals:")
    print(confidence_intervals1)
    print("\nexp1 model_error_list:")
    print(model_error_list1)
    plot1(axs[0], confidence_intervals1)

    # 加载 exp2 数据，并绘制右侧图（Accuracy 图）
    model_acc_list2, confidence_intervals2 = load_data2()
    print("exp2 confidence_intervals:")
    print(confidence_intervals2)
    print("\nexp2 model_acc_list:")
    print(model_acc_list2)
    plot2(axs[1], confidence_intervals2)

    plt.tight_layout()
    plt.savefig('section5-2-1entire-pk_mn.png', dpi=300, bbox_inches='tight')
    plt.savefig('section5-2-1entire-pk_mn.pdf', dpi=300, bbox_inches='tight', format='pdf')
    plt.show()
