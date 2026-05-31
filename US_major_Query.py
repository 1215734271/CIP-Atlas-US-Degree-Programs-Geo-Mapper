import pandas as pd
import os

def extract_ai_universities():
    # 1. 定义文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hd2024_path = os.path.join(current_dir, "hd2024.csv")
    c2024_a_path = os.path.join(current_dir, "c2024_a.csv")
    output_path = os.path.join(current_dir, "US_DS_Universities.csv")

    ai_cipcode = '30.7001'  # 专业代码
    ai_major_name = 'Data Science'

    print("开始读取数据...")
    
    # 2. 读取 c2024_a.csv (专业授予数据)
    # 因为只需要 UNITID 和 CIPCODE，只读取这两列可以节省内存和提升速度
    # CIPCODE 在数据中可能包含多余的空格或被识别为数字/字符串混合，这里统一作为字符串读取
    df_majors = pd.read_csv(c2024_a_path, usecols=['UNITID', 'CIPCODE'], dtype={'UNITID': int, 'CIPCODE': str})

    # 清理 CIPCODE 中的空白字符（如果有）
    df_majors['CIPCODE'] = df_majors['CIPCODE'].str.strip()

    # 3. 过滤出开设人工智能专业的记录，并提取不重复的大学代码
    df_ai_majors = df_majors[df_majors['CIPCODE'] == ai_cipcode]
    unique_ai_unitids = df_ai_majors[['UNITID']].drop_duplicates()

    print(f"找到 {len(unique_ai_unitids)} 所开设{ai_major_name} ({ai_cipcode}) 专业的大学。")

    # 4. 读取 hd2024.csv (大学基本信息数据)
    # 只需要读取 UNITID, INSTNM (大学名称), STABBR (州), LONGITUD (经度), LATITUDE (纬度)
    df_institutions = pd.read_csv(
        hd2024_path, 
        usecols=['UNITID', 'INSTNM', 'STABBR', 'LONGITUD', 'LATITUDE'],
        dtype={'UNITID': int, 'INSTNM': str, 'STABBR': str, 'LONGITUD': float, 'LATITUDE': float},
        encoding='utf-8-sig' # IPEDS 文件通常可能包含非标准字符，utf-8-sig 可以处理 BOM
    )

    # 5. 将有该专业的大学代码与大学基本信息进行匹配合并 (Inner Join)
    result_df = pd.merge(unique_ai_unitids, df_institutions, on='UNITID', how='inner')

    # 6. 添加专业代码和专业名称列
    result_df['专业代码'] = ai_cipcode
    result_df['专业名称'] = ai_major_name

    # 7. 重命名列以符合要求，并调整列的顺序
    result_df = result_df.rename(columns={
        'UNITID': '大学代码',
        'INSTNM': '大学名称',
        'STABBR': '州',
        'LONGITUD': '经度',
        'LATITUDE': '纬度'
    })
    
    # 调整列顺序: “大学代码”，“大学名称”，“州”，“专业代码”，“专业名称”，“经度”，“纬度”
    final_columns = ['大学代码', '大学名称', '州', '专业代码', '专业名称', '经度', '纬度']
    result_df = result_df[final_columns]

    # 8. 保存为新的 CSV 文件
    result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"提取完成！结果已保存至: {output_path}")

if __name__ == "__main__":
    extract_ai_universities()
