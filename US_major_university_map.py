import pandas as pd
import seaborn as sns
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ThemeType, ChartType
import os

def create_map():
    major_name = "Robotics Engineering"      # 专业全称 (用于图表标题和图例)
    major_abbr = "RE"                # 专业缩写 (用于输入和输出文件名)

    # 1. 导入和清洗数据
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, f"US_{major_abbr}_Universities.csv")
    if not os.path.exists(input_path):
        print(f"Error: 找不到文件 {input_path}")
        return

    df = pd.read_csv(input_path)
    
    # 映射州缩写(STABBR)到州全称，以适配 pyecharts 地图
    us_states_map = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia', 
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 
        'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
        'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
        'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 
        'WY': 'Wyoming', 'PR': 'Puerto Rico'
    }
    
    df['州全称'] = df['州'].map(us_states_map)
    df_clean = df.dropna(subset=['大学名称', '州全称', '经度', '纬度']).copy()
    df_clean = df_clean.drop_duplicates(subset=['大学名称'])

    # 统计各州数量
    state_counts = df_clean['州全称'].value_counts().to_dict()
    max_val = max(state_counts.values()) if state_counts else 1
    min_val = min(state_counts.values()) if state_counts else 0

    print(f"清洗完成，共有 {len(df_clean)} 所开设该专业的高校。")

    # 2. 准备专业蓝色系热力配置 (Seaborn Blues)
    palette = sns.color_palette("Blues", n_colors=100).as_hex()
    default_light_blue = palette[5]  # 取序列中极浅的蓝色作为无数据州的底色

    regions_config = []
    for state, count in state_counts.items():
        if max_val > min_val:
            idx = int((count - min_val) / (max_val - min_val) * 94) + 5
        else:
            idx = 50
        regions_config.append({
            "name": state,
            "itemStyle": {"areaColor": palette[idx], "opacity": 1}
        })

    # 3. 构建并渲染美国高校分布图
    geo = (
        Geo(init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT, 
            bg_color="#ffffff", 
            width="1000px", 
            height="750px"
        ))
        .add_schema(
            maptype="美国",
            is_roam=False,
            itemstyle_opts=opts.ItemStyleOpts(color=default_light_blue, border_color="#003366", border_width=1)
        )
    )

    # 注册经纬度坐标并添加大学散点
    for _, row in df_clean.iterrows():
        geo.add_coordinate(row['大学名称'], float(row['经度']), float(row['纬度']))

    geo.add(
        f"University with {major_name} Programs",
        [(row['大学名称'], 1) for _, row in df_clean.iterrows()],
        type_=ChartType.SCATTER,
        symbol_size=7,
        itemstyle_opts=opts.ItemStyleOpts(color="rgba(0, 32, 96, 0.7)"),
        label_opts=opts.LabelOpts(is_show=False)
    )

    # 手动注入州的热力颜色配置
    geo.options["geo"]["regions"] = regions_config

    geo.set_global_opts(
        title_opts=opts.TitleOpts(
            title=f"US {major_name} University Distribution",
            pos_left="center",
            pos_top="30px",
            title_textstyle_opts=opts.TextStyleOpts(color="#333", font_size=26)
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_piecewise=False,
            min_=min_val,
            max_=max_val,
            range_color=sns.color_palette("Blues", n_colors=6).as_hex(),
            range_text=["High", "Low"],
            pos_left="5%",
            pos_bottom="10%",
            textstyle_opts=opts.TextStyleOpts(color="#333"),
            series_index=1 # 避开散点系列
        ),
        legend_opts=opts.LegendOpts(
            is_show=True, 
            pos_bottom="5%", 
            pos_left="center",
            textstyle_opts=opts.TextStyleOpts(color="#333")
        )
    )

    output_html = os.path.join(current_dir, f"us_{major_abbr.lower()}_university_map.html")
    geo.render(output_html)
    print(f"地图已生成并保存为：{output_html}")

if __name__ == '__main__':
    create_map()
