import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.figsize": (7, 4),
    "font.size": 12,
    "axes.edgecolor": "black",
    "axes.linewidth": 1.5,
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
})

models = ["GPT", "Gemini", "internvl8B", "internvl40B"]
width = 0.35

data = {
    "Experiment 1": {
        "baseline": np.array([0.33, 0.36, 0.324, 0.333]),
        "cot": np.array([0.262, 0.364, 0.31, 0.326]),
        "transform": lambda x: np.log2(x * 100),
        "ylabel": "log2(error)"
    },
    "Experiment 2": {
        "baseline": np.array([49.333, 81.795, 49.944, 49.944]),
        "cot": np.array([68.333, 82.056, 58.278, 45.444]),
        "transform": lambda x: x,
        "ylabel": "Accuracy"
    },
    "Experiment 3": {
        "baseline": np.array([18.21, 22.296, 17.045, 16.831]),
        "cot": np.array([19.259, 18.37, 16.412, 18.889]),
        "transform": lambda x: x,
        "ylabel": "Accuracy"
    }
}


def plot_exp(title, cfg):
    x = np.arange(len(models))
    baseline = cfg["transform"](cfg["baseline"])
    cot = cfg["transform"](cfg["cot"])

    fig, ax = plt.subplots()
    ax.bar(x - width/2, baseline, width, label="Baseline", color="#1f77b4")
    ax.bar(x + width/2, cot, width, label="CoT", color="#ff7f0e")

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=30, ha="right")
    ax.set_ylabel(cfg["ylabel"])
    ax.set_title(title)
    ax.grid(True)

    ax.legend(
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=False
    )

    plt.tight_layout()
    plt.show()

for exp_name, cfg in data.items():
    plot_exp(exp_name, cfg)
