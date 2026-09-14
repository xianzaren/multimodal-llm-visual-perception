import pandas as pd

df = pd.read_csv("./static/Data/data1.csv", header=None, skiprows=1, sep=",")
print(f"CSV 形状: {df.shape}")
print(df.head())

