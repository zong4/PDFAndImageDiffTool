import pdfplumber
from difflib import Differ
import sys
from PIL import Image
import os
import webbrowser
import pytesseract


def extract_text_from_image(image_path):
    """从图片中提取文本"""
    # 设置 Tesseract 的 OCR 参数
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'

    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, config=custom_config)
    print(f"从图片中提取的文本：\n{text}")
    return text


def extract_text_from_pdf(pdf_path):
    """从 PDF 文件中提取文本"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


def compare_text(text1, text2):
    """比较两个文本的差异，返回差异结果"""
    differ = Differ()
    diff = list(differ.compare(text1.splitlines(), text2.splitlines()))
    return diff


def generate_html_diff(diff_result, file1_path, file2_path, output_path):
    """将差异结果生成 HTML 文件，类似于 VSCode 的 Git Diff 视图"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Diff</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
            }}
            .diff-container {{
                display: flex;
                width: 100%;
            }}
            .diff-left, .diff-right {{
                width: 50%;
                overflow-x: auto;
                padding: 10px;
                box-sizing: border-box;
            }}
            .diff-left {{
                background-color: #f0f0f0;
            }}
            .diff-right {{
                background-color: #fafafa;
            }}
            .line {{
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 14px;
                line-height: 1.5;
            }}
            .added {{
                background-color: #a6f3a6;
            }}
            .removed {{
                background-color: #f8c6c6;
            }}
        </style>
    </head>
    <body>
        <div class="diff-container">
            <div class="diff-left">
                <h3>{file1_path}</h3>
                {left_content}
            </div>
            <div class="diff-right">
                <h3>{file2_path}</h3>
                {right_content}
            </div>
        </div>
    </body>
    </html>
    """

    left_lines = []
    right_lines = []
    for line in diff_result:
        if line.startswith("  "):  # 未修改的行
            left_lines.append(f'<div class="line">{line[2:]}</div>')
            right_lines.append(f'<div class="line">{line[2:]}</div>')
        elif line.startswith("- "):  # 删除的行
            left_lines.append(f'<div class="line removed">{line[2:]}</div>')
            right_lines.append(f'<div class="line"></div>')  # 右侧对应空白行
        elif line.startswith("+ "):  # 新增的行
            left_lines.append(f'<div class="line"></div>')  # 左侧对应空白行
            right_lines.append(f'<div class="line added">{line[2:]}</div>')

    left_content = "\n".join(left_lines)
    right_content = "\n".join(right_lines)

    html_content = html_content.format(
        file1_path=file1_path,
        file2_path=file2_path,
        left_content=left_content,
        right_content=right_content
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"差异结果已保存到 {output_path}")


def is_image_file(file_path):
    """检查文件是否为图片"""
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    return any(file_path.lower().endswith(ext) for ext in image_extensions)


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_pdfs.py <file1> <file2>")
        return

    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    output_path = "output/diff_output.html"

    # 如果有图片，则设置 Tesseract 路径
    if is_image_file(file1_path) or is_image_file(file2_path):
        pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.5.0/bin/tesseract'

    # 提取文本
    if is_image_file(file1_path):
        text1 = extract_text_from_image(file1_path)
    else:
        text1 = extract_text_from_pdf(file1_path)

    if is_image_file(file2_path):
        text2 = extract_text_from_image(file2_path)
    else:
        text2 = extract_text_from_pdf(file2_path)

    # 比较文本并生成 HTML 差异结果
    diff_result = compare_text(text1, text2)
    generate_html_diff(diff_result, file1_path, file2_path, output_path)

    # 自动打开生成的HTML文件
    if os.name == "nt":  # Windows
        os.startfile(output_path)
    elif os.name == "posix":  # macOS 或 Linux
        os.system(f"open {output_path}" if os.uname().sysname == "Darwin" else f"xdg-open {output_path}")


if __name__ == "__main__":
    main()