from bs4 import BeautifulSoup
import hashlib
import sys
import html


def compare_html_files(file1, file2, output_filename, is_strict):
    """比较两个HTML文件的内容差异并生成对比报告"""
    # 解析文件内容为块列表
    blocks1 = parse_blocks(file1, is_strict)
    blocks2 = parse_blocks(file2, is_strict)

    # 计算哈希集合用于快速查找
    hashes1 = {hashlib.md5(block.encode()).hexdigest() for block in blocks1}
    hashes2 = {hashlib.md5(block.encode()).hexdigest() for block in blocks2}

    # 生成左右列HTML内容
    left_content = generate_column_content(blocks1, hashes2, is_strict)
    right_content = generate_column_content(blocks2, hashes1, is_strict)

    # 构建完整的HTML报告
    html_report = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>HTML Diff Report</title>
        <style>
            .container {{
                display: flex;
                width: 100%;
                font-family: Arial, sans-serif;
            }}
            .column {{
                flex: 1;
                padding: 20px;
                border: 1px solid #ddd;
                background: #f9f9f9;
                overflow-wrap: break-word;
            }}
            .diff {{
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                margin: 5px 0;
                padding: 10px;
            }}
            h2 {{
                color: #333;
                border-bottom: 2px solid #666;
                padding-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="column">
                <h2>{sys.argv[1]}</h2>
                {"".join(left_content)}
            </div>
            <div class="column">
                <h2>{sys.argv[2]}</h2>
                {"".join(right_content)}
            </div>
        </div>
    </body>
    </html>
    '''

    # 写入输出文件
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_report)


def generate_column_content(blocks, other_hashes, is_strict):
    """生成带差异标记的列内容"""
    content = []
    for block in blocks:
        if not is_strict:
            display_content = block
        else:
            display_content = block
        
        # 判断是否是唯一块
        block_hash = hashlib.md5(block.encode()).hexdigest()
        if block_hash not in other_hashes:
            content.append(f'<div class="diff">{display_content}</div>')
        else:
            content.append(f'<div>{display_content}</div>')
    return content


def parse_blocks(html_file, is_strict):
    """解析HTML并返回标准化内容块列表（保留原始顺序）"""
    soup = BeautifulSoup(html_file, 'html.parser')
    blocks = []

    if not is_strict:
        # 提取主要块级元素
        for tag in soup.find_all(['p', 'ol', 'ul', 'pre', 'table']):
            content = tag
            blocks.append(content)
    else:
        # 提取次要块级元素
        for tag in soup.find_all(['p', 'li', 'code', 'tr']):
            # 剔除tag里的属性
            for attr in ['class', 'style', 'id', 'width', 'height']:
                if tag.has_attr(attr):
                    del tag[attr]

            # 剔除tag里的所有空白字符
            tag = html.unescape(str(tag))
            tag = tag.replace('\n', '')
            tag = tag.replace('\t', '')
            tag = tag.replace(' ', '')

            # 剔除tag里的首尾空白字符
            # tag.string = tag.get_text().strip()

            content = tag
            blocks.append(content)
    return blocks


def alter_file_to_html(filename):
    """统一文件扩展名为html"""
    if filename.endswith('.html'):
        return filename
    return f"{filename.rsplit('.', 1)[0]}.html"


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python compare.py <file1> <file2>")
        sys.exit(1)

    # 处理文件名并读取内容
    file1_path = alter_file_to_html(sys.argv[1])
    file2_path = alter_file_to_html(sys.argv[2])
    
    with open(file1_path, 'r', encoding='utf-8') as f:
        file1_content = f.read()
    
    with open(file2_path, 'r', encoding='utf-8') as f:
        file2_content = f.read()

    # 执行比较并生成报告
    output_filename = "./output/diff.html"
    is_strict = True
    compare_html_files(
        file1_content, 
        file2_content,
        output_filename=output_filename,
        is_strict=is_strict
    )
    print("对比报告已生成：{}".format(output_filename))