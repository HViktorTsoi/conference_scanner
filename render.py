import os
import bibtexparser
import xlsxwriter
import tqdm


# 定义函数以读取.bib文件并写入Excel
def bib_to_excel(input_dir, output_excel, filename_filter):
    # 创建Excel文件
    workbook = xlsxwriter.Workbook(output_excel)

    # 获取所有包含"MobiCom"的.bib文件，按字典序排序
    bib_files = list(reversed(sorted(
        [os.path.join(input_dir, f) for f in os.listdir(input_dir) if filename_filter in f and f.endswith('.bib')]
    )))

    for bib_file in tqdm.tqdm(bib_files):
        # 获取sheet名称（去除扩展名）
        sheet_name = os.path.splitext(os.path.basename(bib_file))[0][:31]  # Excel sheet名最多31字符
        worksheet = workbook.add_worksheet(sheet_name)

        # 定义表头格式（加粗）
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1  # 添加边框
        })

        # 添加表头
        headers = ['Select?', 'Title', 'Abstract', 'URL', 'Authors']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        # 添加条件格式：如果第一列为YES，整行背景色变为浅绿色
        worksheet.conditional_format(1, 0, 1000, 4, {
            'type': 'formula',
            'criteria': '=$A2="YES"',
            'format': workbook.add_format({'bg_color': '#C6EFCE'})
        })

        row_num = 1  # 当前写入的行号

        # 打开.bib文件并解析
        with open(bib_file, 'r', encoding='utf-8') as bib_file_obj:
            bib_database = bibtexparser.load(bib_file_obj)

            # 遍历每篇论文
            for entry in bib_database.entries:
                title = entry.get('title', '无标题')
                abstract = entry.get('abstract', '无摘要')
                authors = entry.get('author', '无作者')
                url = entry.get('url', '无URL')

                # 添加下拉列表
                worksheet.data_validation(row_num, 0, row_num, 0, {
                    'validate': 'list',
                    'source': ['YES', 'NO'],
                    # 'input_message': 'YES or NO',
                    'error_message': '"YES" or "NO"'
                })

                # 写入论文信息
                worksheet.write(row_num, 1, title,
                                workbook.add_format(
                                    {'border': 1, 'valign': 'vcenter', 'text_wrap': True, 'bold': True, }))
                worksheet.write(row_num, 2, abstract,
                                workbook.add_format({'border': 1, 'valign': 'vcenter', 'text_wrap': True}))
                worksheet.write(row_num, 3, url,
                                workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', }))
                worksheet.write(row_num, 4, authors,
                                workbook.add_format({'border': 1, 'valign': 'vcenter', }))
                worksheet.set_row(row_num, None,
                                  workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'border': 3, }))
                row_num += 1

        # 设置列宽
        worksheet.set_column(1, 1, 35)
        worksheet.set_column(2, 2, 75)
        worksheet.set_column(3, 4, 35)

        # 冻结首行 这样在腾讯文档中可以正确显示title
        worksheet.freeze_panes(1, 0)  # 冻结首行

    # 关闭Excel文件
    workbook.close()


# 示例调用
input_bib_dir = 'bibtex'  # 替换为实际的.bib文件目录路径

for filename_filter in ['MobiCom', 'MobiSys', 'SenSys', 'IPSN']:
    output_excel_file = './output/{}.xlsx'.format(filename_filter)
    bib_to_excel(input_bib_dir, output_excel_file, filename_filter)
