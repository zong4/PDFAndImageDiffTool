import pdfplumber
import re
from bs4 import BeautifulSoup


def pdf_to_html(pdf_path, html_path):
    soup = BeautifulSoup(features="html.parser")
    html = soup.new_tag("html")
    soup.append(html)
    body = soup.new_tag("body")
    html.append(body)

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 优先处理表格（使用精确线条检测）
            tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "explicit_vertical_lines": page.curves + page.edges
            })
            
            for table in tables:
                if len(table) > 0 and len(table[0]) > 0:
                    build_table(table, body, soup)
            
            # 处理文本内容
            text = page.extract_text()
            current_list = None
            
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # 列表处理
                list_type = get_list_type(line)
                if list_type:
                    current_list = handle_list(line, list_type, body, soup, current_list)
                else:
                    if current_list:
                        current_list = None
                    # 代码块检测
                    if re.match(r"^\s{4,}|```", line):
                        handle_code(line, body, soup)
                    # 标题检测
                    elif re.match(r"^H[1-6]\s+", line):
                        handle_heading(line, body, soup)
                    else:
                        add_paragraph(line, body, soup)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))


def build_table(table_data, body, soup):
    print(table_data)
    """核心表格构建"""
    table = soup.new_tag("table")
    thead = soup.new_tag("thead")
    tbody = soup.new_tag("tbody")
    
    # 自动处理表头
    if table_data:
        header = table_data[0]
        tr = soup.new_tag("tr")
        for col in header:
            th = soup.new_tag("th")
            th.string = str(col).strip()
            tr.append(th)
        thead.append(tr)
        
        # 处理内容行
        for row in table_data[1:]:
            tr = soup.new_tag("tr")
            for col in row:
                td = soup.new_tag("td")
                td.string = str(col).strip()
                tr.append(td)
            tbody.append(tr)
    
    table.append(thead)
    table.append(tbody)
    body.append(table)


def get_list_type(line):
    """精确列表类型检测"""
    if re.match(r"^\d+\.\s", line):
        return "ol"
    elif re.match(r"^[\u2022•\-*]\s", line):
        return "ul"
    return None


def handle_list(line, list_type, body, soup, current_list):
    """列表处理"""
    if not current_list or current_list.name != list_type:
        current_list = soup.new_tag(list_type)
        body.append(current_list)
    
    # 提取列表内容
    content = re.sub(r"^[\d•\-*]+\.?\s*", "", line)
    li = soup.new_tag("li")
    li.string = content.strip()
    current_list.append(li)
    return current_list


def handle_code(line, body, soup):
    """代码块处理"""
    pre = soup.new_tag("pre")
    code = soup.new_tag("code")
    code.string = line.strip()
    pre.append(code)
    body.append(pre)


def handle_heading(line, body, soup):
    """标题处理"""
    level = int(line[1]) if line[1].isdigit() else 6
    tag = f"h{level}" if 1 <= level <=6 else "h6"
    heading = soup.new_tag(tag)
    heading.string = line[3:].strip()
    body.append(heading)


def add_paragraph(line, body, soup):
    """普通段落"""
    p = soup.new_tag("p")
    p.string = line
    body.append(p)


# 使用示例
pdf_to_html("./input/11.pdf", "output.html")