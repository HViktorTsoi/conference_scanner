import os
import bibtexparser

# 定义函数以提取并格式化bib文件内容
def process_bib_files(input_dir, output_file):
    # 打开Markdown文件以写入
    with open(output_file, 'w', encoding='utf-8') as md_file:
        md_file.write("# 论文列表\n\n")

        # 遍历指定路径下的所有.bib文件
        for file_name in os.listdir(input_dir):
            if file_name.endswith('.bib'):
                file_path = os.path.join(input_dir, file_name)

                # 读取.bib文件
                with open(file_path, 'r', encoding='utf-8') as bib_file:
                    bib_database = bibtexparser.load(bib_file)

                    # 遍历每篇论文
                    for entry in bib_database.entries:
                        title = entry.get('title', '无标题').replace('<', '\\<')
                        abstract = entry.get('abstract', '无摘要').replace('<', '\\<')
                        year = entry.get('year', '无年份').replace('<', '\\<')
                        conference = entry.get('booktitle', '无会议名称').replace('<', '\\<')

                        # 写入Markdown文件
                        md_file.write(f"## {title}\n\n")
                        md_file.write(f"- **会议名称**: {conference}\n")
                        md_file.write(f"- **年份**: {year}\n")
                        md_file.write(f"- **摘要**: {abstract}\n\n")

# 指定输入路径和输出文件
input_directory = "bibtex"
output_markdown = "output.md"

# 调用函数
process_bib_files(input_directory, output_markdown)

# 在bibtex下创建一组空的bib文件，命名方式为['MobiCom', 'MobiSys', 'SenSys', 'IPSN']与[2025,2024,2023,2022...,]
