import os

from utils import extract_color_from_filename
from utils import client, get_image_dict1


color_map_configs = {
    'gray': {
        "name": "gray",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色",
        "Ranges": "[(255,255,255), (202,202,202), (151,151,151), (100,100,100), (49,49,49)]"
    },
    'hot': {
        "name": "hot",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色",
        "Ranges": "[(255,255,255), (255,255,54), (255,160,0), (242,17,0), (135,0,0)]"
    },
    "rainbow": {
        "name": "rainbow",
        "bottom_color": "purple",
        "top_color": "red",
        "legend": "紫色到红色",
        "Ranges":"[(255,0,0),(254,149,79),(178,242,149),(73,240,207),(25,149,241)]"
    },
    "Blues": {
        "name": "Blues_r",
        "bottom_color": "dark blue",
        "top_color": "pale blue",
        "legend": "深蓝到浅蓝",
        "Ranges": "[(255,255,255),(207,224,24),(145,195,22),(73,150,200),(21,97,168)]"
    },
    "coolwarm": {
        "name": "coolwarm",
        "bottom_color": "blue",
        "top_color": "red",
        "legend": "红色到蓝色",
        "Ranges": "[(176,4,37),(236,130,10),(240,201,18),(190,210,24),(122,157,24)]"
    },
    "blueyellow": {
        "name": "从blue到yellow的自定义颜色映射表",
        "bottom_color": "blue",
        "top_color": "yellow",
        "legend": "蓝色到黄色",
        "Ranges": "[(255,255,0), (202,202,52), (151,151,10), (100,100,15), (47,47,205)]"
    },
    "cubehelix": {
        "name": "cubehelix",
        "bottom_color": "very dark blue",
        "top_color": "white",
        "legend": "深蓝到白色",
        "Ranges": "[(255,255,255), (193,202,243), (208,126,147), (84,121,47), (22,58,78)]"
    },
    "magma": {
        "name": "magma",
        "bottom_color": "very dark purple",
        "top_color": "light yellow",
        "legend": "深紫到明黄",
        "Ranges": "[(252,251,189), (254,159,109), (221,73,104), (139,41,128), (57,15,110)]"
    },
    "spectral": {
        "name": "nipy_spectral",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色",
        "Ranges":"[(204,188,188), (255,153,0), (0,255,0), (0,170,136), (0,0,220)]"
    },
}

color = 'hot'
frequency = '7'
png_paths = f"E:\桌面\Final project//resultexp1\exp1s\{color}\ScalarField_{color}_(630, 820)_(7, 7)_5.png"
#png_paths = f"E:\桌面\Final project\color\exp1\exp1s\{color}\ScalarField_{color}_(630, 820)_(7, 7)_5.png"
# 获取colormap_name
colormap_name = extract_color_from_filename(png_paths)
# 获取相应参数
colormap = color_map_configs[colormap_name]
name = colormap['name']
bottom_color = colormap['bottom_color']
top_color = colormap['top_color']
legend = colormap['legend']
RGB = colormap['Ranges']

# 设置message头
messages = [
    {"role": "system", "content": f"这张图是一张标量场可视化图像"
                                  #f"请分析图例中颜色与数值的对应关系"
                                  #f"你需要根据图例中颜色与数值的对应关系在左侧标量场可视化图像中找到特定值对应的坐标"
                                  f"整张图片横向长度为820pixel，纵向宽度为630pixel，设左下角坐标为(0,0)。"
                                  f"请你告诉我数值在1.0,0.8,0.6,0.4,0.2,0.0的点的位置"
                                  f"值为1.0, 0.8, 0.6, 0.4, 0.2对应的RGB值分别为{RGB}"
                                  f"横轴向右为x正方向，纵轴向上为y正方向"
                                  f"请告诉我你完成这个任务过程中的思考和你使用的算法逻辑，比如CNN等"
                                  #f"设图像左下角为坐标轴原点，请给出这六个颜色的点的坐标"
                                  #f"step1:"
                                  #f"整张图片横向长度为1006，纵向宽度为621，"
                                  #f"请在图上根据图例中给出的颜色定位标量场图像，"
                                  #f"并告诉我标量场图像的大小是多少,即长宽是多少"
                                  #f"step2:"
                                  #f"这张图分为位于左侧的标量场可视化图像和位于右侧颜色图例，右侧标有数字的colorbar为图例"
                                  #f"请分析右侧的图例，将值与颜色对应起来"
                                  #f"最后请告诉我值1.0,0.8,0.6,0.4,0.2,0.0值的颜色和RGB是什么？"
     }
]

# 编码后的 batch 张图片
images = get_image_dict1(png_paths)

messages.append({"role": "user", "content": images})

# 给gpt说明要求
user_input = "根据我的要求给我相应的结果 格式不变 不要markdown格式加粗"
messages.append(
    {"role": "user", "content": user_input}
)

# 返回结果
completion = client.chat.completions.create(model="gpt-4o", messages=messages)
answer = completion.choices[0].message.content
print('System:', answer)
