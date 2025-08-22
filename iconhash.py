import time
import hashlib
import base64
import mmh3
from openpyxl.styles import Font
import os
import favicon
import requests
from PIL import Image
from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.drawing.image import Image

UA = "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"

# 创建xlsx文件
wb = Workbook()
sheet = wb.active
header_data = ["url", "icon", "hunter", "fofa", "type", "ico_url"]

sheet.column_dimensions['A'].width = 30
sheet.column_dimensions['B'].width = 10
sheet.column_dimensions['C'].width = 50
sheet.column_dimensions['D'].width = 25
sheet.column_dimensions['E'].width = 8
sheet.column_dimensions['F'].width = 80
sheet.append(header_data)
bold_font = Font(bold=True)
for cell in sheet[1]:  # sheet[1]表示第一行
    cell.font = bold_font
xlsx_filename = (f"icons_{time.time()}.xlsx")
wb.save(xlsx_filename)


def get_icon(url):
    headers = {'User-Agent': UA, 'referer': url}
    icon = favicon.get(url, headers=headers, timeout=5, verify=False)
    return icon


def save_icon(icon):
    headers = {'User-Agent': UA, 'referer': icon.url}
    response = requests.get(icon.url, headers=headers, timeout=5, verify=False)
    iconname = time.time()
    save_dir = "./icons"
    try:
        os.makedirs(save_dir, exist_ok=True)
    except OSError as e:
        print(f"创建目录失败：{e}")
        return False
    # 保存图片到本地
    save_path = f"./icons/{iconname}.{icon.format}"  # 图片保存路径
    with open(save_path, 'wb') as f:  # 以二进制写入文件保存
        f.write(response.content)

    return save_path


def save_xlsx(url, icon, type, ico_url, filepath):
    hunter = get_image_md5(icon)
    fofa = get_image_fofa(icon)
    workbook = load_workbook(filepath)
    sheet = workbook.active
    data = [url, None, hunter, fofa, type,ico_url]
    sheet.append(data)
    lines = sheet.max_row
    # 加载图片
    img = Image(icon)
    # 将图片添加到指定位置
    sheet.add_image(img, f"B{lines}")
    sheet.row_dimensions[lines].height = 20
    workbook.save(filepath)

    return ico_url


def get_image_md5(file_path):
    try:
        # 创建MD5哈希对象
        md5_hash = hashlib.md5()

        # 以二进制模式分块读取文件
        with open(file_path, "rb") as f:
            # 分块读取避免大文件内存问题
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        hunter_hash = md5_hash.hexdigest()
        hunter = f'web.icon = "{hunter_hash}"'

        return hunter

    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    except OSError as e:
        raise OSError(f"无法读取文件: {str(e)}")


def get_image_fofa(file_path):
    with open(file_path, "rb") as f:
        # 分块读取避免大文件内存问题
        image_base64 = base64.encodebytes(f.read())
        fofa_hash = mmh3.hash(image_base64)
        f.close()
        fofa = f'icon_hash="{fofa_hash}"'
    return fofa


def input_url(url):
    icon = get_icon(url)
    print(f"获取{url}图标")
    for i in icon:
        img_path = save_icon(i)
        save_xlsx(url, img_path, i.format, i.url, xlsx_filename)


def read_file(file_path):
    lines = []

    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return lines

        # 检查是否为文件
        if not os.path.isfile(file_path):
            print(f"错误: '{file_path}' 不是一个文件")
            return lines

        # 打开文件并按行读取
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                # 移除行尾的换行符
                cleaned_line = line.rstrip('\n\r')
                lines.append(cleaned_line)
        print(f"\n成功读取文件，共 {len(lines)} 行")
        return lines
    except UnicodeDecodeError:
        print("文件打开失败")


for i in read_file("t.txt"):
    input_url(i)
