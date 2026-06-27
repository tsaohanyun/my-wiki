---
title: Python自动化办公
aliases:
  - Python自动化办公
  - Office Automation
tags:
  - python
  - automation
  - office
  - excel
  - word
  - pdf
  - email
type: wiki
status: published
created: 2026-06-28
updated: 2026-06-28
source: ""
difficulty: intermediate
project: AI-Agent
---

# Python自动化办公

Python在办公自动化领域有着强大的生态系统，能够高效处理Excel、Word、PDF等文档，并实现邮件自动化发送。

## 1. Excel处理

### 1.1 使用openpyxl处理Excel文件

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
import pandas as pd

# 创建工作簿
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "销售数据"

# 写入数据
headers = ["产品", "Q1", "Q2", "Q3", "Q4", "总计"]
ws.append(headers)

data = [
    ["笔记本电脑", 120, 135, 148, 160, None],
    ["智能手机", 250, 280, 310, 350, None],
    ["平板电脑", 80, 95, 110, 125, None],
    ["耳机", 180, 200, 220, 250, None],
]

for row in data:
    ws.append(row)

# 添加公式计算总计
for row in range(2, 6):
    ws.cell(row=row, column=6).value = f"=SUM(B{row}:E{row})"
    ws.cell(row=row, column=6).number_format = '#,##0'

# 格式化标题行
header_font = Font(name='微软雅黑', size=12, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
header_alignment = Alignment(horizontal='center', vertical='center')

for col in range(1, 7):
    cell = ws.cell(row=1, column=col)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_alignment

# 设置列宽
for col in range(1, 7):
    ws.column_dimensions[get_column_letter(col)].width = 15

# 添加边框
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

for row in ws.iter_rows(min_row=1, max_row=5, min_col=1, max_col=6):
    for cell in row:
        cell.border = thin_border

# 创建图表
chart = BarChart()
chart.title = "季度销售趋势"
chart.x_axis.title = "产品"
chart.y_axis.title = "销量"
chart.style = 10

data_ref = Reference(ws, min_col=2, min_row=1, max_col=5, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4
ws.add_chart(chart, "A8")

# 保存文件
wb.save('sales_report.xlsx')
print("Excel文件已生成：sales_report.xlsx")
```

### 1.2 使用pandas处理Excel

```python
import pandas as pd
import numpy as np

# 读取Excel文件
df = pd.read_excel('sales_report.xlsx', sheet_name='销售数据')

# 数据处理
df['同比增长'] = np.random.uniform(0.05, 0.15, size=len(df))
df['目标完成率'] = df['总计'] / (df['总计'].mean() * 1.1)

# 数据透视表
pivot_df = df.pivot_table(
    values=['Q1', 'Q2', 'Q3', 'Q4'],
    index=['产品'],
    aggfunc='sum'
)

# 导出到多个sheet
with pd.ExcelWriter('processed_sales.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='原始数据', index=False)
    pivot_df.to_excel(writer, sheet_name='数据透视')
    
    # 创建汇总表
    summary = pd.DataFrame({
        '指标': ['总销售额', '平均季度销售额', '最高销量产品', '最低销量产品'],
        '数值': [
            df['总计'].sum(),
            df[['Q1', 'Q2', 'Q3', 'Q4']].mean().mean(),
            df.loc[df['总计'].idxmax(), '产品'],
            df.loc[df['总计'].idxmin(), '产品']
        ]
    })
    summary.to_excel(writer, sheet_name='汇总', index=False)

print("数据处理完成：processed_sales.xlsx")
```

## 2. Word文档操作

### 2.1 使用python-docx创建Word文档

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
import datetime

def create_report():
    doc = Document()
    
    # 设置文档样式
    style = doc.styles['Normal']
    font = style.font
    font.name = '微软雅黑'
    font.size = Pt(11)
    
    # 添加标题
    title = doc.add_heading('年度销售报告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加段落
    p = doc.add_paragraph()
    p.add_run('报告日期：').bold = True
    p.add_run(datetime.datetime.now().strftime('%Y年%m月%d日'))
    
    p = doc.add_paragraph()
    p.add_run('报告人：').bold = True
    p.add_run('数据分析部')
    
    doc.add_paragraph('')
    
    # 添加二级标题
    doc.add_heading('一、销售概况', level=1)
    
    # 添加带格式的段落
    p = doc.add_paragraph()
    run = p.add_run('本年度公司销售额达到')
    run.font.size = Pt(12)
    run = p.add_run(' 1,250万元 ')
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 112, 192)
    run.bold = True
    run = p.add_run('，同比增长15.3%。')
    run.font.size = Pt(12)
    
    # 添加表格
    doc.add_heading('二、产品销售明细', level=1)
    
    table = doc.add_table(rows=5, cols=5)
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # 表头
    headers = ['产品', 'Q1', 'Q2', 'Q3', 'Q4']
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.paragraphs[0].runs[0].font.bold = True
    
    # 数据
    data = [
        ['笔记本电脑', '120', '135', '148', '160'],
        ['智能手机', '250', '280', '310', '350'],
        ['平板电脑', '80', '95', '110', '125'],
        ['耳机', '180', '200', '220', '250'],
    ]
    
    for i, row_data in enumerate(data):
        for j, value in enumerate(row_data):
            table.rows[i + 1].cells[j].text = value
    
    # 添加列表
    doc.add_heading('三、关键发现', level=1)
    
    findings = [
        '智能手机是销售额最高的产品线',
        '耳机产品增长最快，同比增长28%',
        'Q4季度整体表现最佳',
        '平板电脑市场份额持续扩大',
    ]
    
    for finding in findings:
        p = doc.add_paragraph(finding, style='List Bullet')
    
    # 添加页脚
    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = '© 2026 公司内部报告 | 机密文件'
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 保存文档
    doc.save('annual_sales_report.docx')
    print("Word文档已生成：annual_sales_report.docx")

create_report()
```

### 2.2 读取和修改现有Word文档

```python
from docx import Document
import re

def modify_existing_doc(input_path, output_path, replacements):
    """批量替换Word文档中的文本"""
    doc = Document(input_path)
    
    for paragraph in doc.paragraphs:
        for old_text, new_text in replacements.items():
            if old_text in paragraph.text:
                # 保留格式的同时替换文本
                for run in paragraph.runs:
                    if old_text in run.text:
                        run.text = run.text.replace(old_text, new_text)
    
    # 替换表格中的文本
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for old_text, new_text in replacements.items():
                    if old_text in cell.text:
                        cell.text = cell.text.replace(old_text, new_text)
    
    doc.save(output_path)
    print(f"文档已修改并保存至：{output_path}")

# 使用示例
replacements = {
    '{{公司名称}}': '科技有限公司',
    '{{报告年份}}': '2026',
    '{{报告人}}': '数据分析部',
}

# modify_existing_doc('template.docx', 'filled_report.docx', replacements)
```

## 3. PDF生成

### 3.1 使用ReportLab生成PDF

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_pdf_report():
    # 注册中文字体（需要下载字体文件）
    # pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
    
    filename = "business_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    
    # 样式定义
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # 居中
        textColor=HexColor('#2E75B6')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        textColor=HexColor('#404040')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=12
    )
    
    # 构建内容
    story = []
    
    # 标题
    story.append(Paragraph("年度业务分析报告", title_style))
    story.append(Spacer(1, 20))
    
    # 日期
    story.append(Paragraph("报告期间：2025年1月 - 2025年12月", body_style))
    story.append(Paragraph("编制日期：2026年6月28日", body_style))
    story.append(Spacer(1, 30))
    
    # 摘要
    story.append(Paragraph("一、执行摘要", subtitle_style))
    story.append(Paragraph(
        "本报告对公司2025年度业务运营情况进行了全面分析。"
        "数据显示，公司整体业绩保持稳定增长态势，"
        "各业务板块均实现预期目标。",
        body_style
    ))
    story.append(Spacer(1, 20))
    
    # 销售数据表格
    story.append(Paragraph("二、销售数据", subtitle_style))
    
    table_data = [
        ['产品类别', 'Q1', 'Q2', 'Q3', 'Q4', '年度总计'],
        ['电子产品', '280', '320', '350', '410', '1360'],
        ['软件服务', '150', '180', '200', '240', '770'],
        ['咨询服务', '90', '110', '130', '160', '490'],
        ['其他业务', '60', '75', '85', '100', '320'],
        ['总计', '580', '685', '765', '910', '2940'],
    ]
    
    table = Table(table_data, colWidths=[80, 60, 60, 60, 60, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9E2F3')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # 关键指标
    story.append(Paragraph("三、关键绩效指标", subtitle_style))
    
    kpi_data = [
        ['指标', '目标值', '实际值', '完成率'],
        ['营业收入', '3000万', '2940万', '98%'],
        ['净利润', '500万', '520万', '104%'],
        ['客户满意度', '90%', '92%', '102%'],
        ['新客户数量', '100家', '115家', '115%'],
    ]
    
    kpi_table = Table(kpi_data, colWidths=[100, 80, 80, 70])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548235')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E2EFDA')]),
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 30))
    
    # 结论
    story.append(Paragraph("四、结论与建议", subtitle_style))
    
    conclusions = [
        "1. 电子产品业务保持强劲增长，建议加大研发投入",
        "2. 软件服务业务利润率最高，可作为重点发展方向",
        "3. 客户满意度持续提升，品牌影响力增强",
        "4. 建议拓展海外市场，寻求新的增长点",
    ]
    
    for conclusion in conclusions:
        story.append(Paragraph(conclusion, body_style))
    
    # 构建PDF
    doc.build(story)
    print(f"PDF报告已生成：{filename}")

create_pdf_report()
```

### 3.2 PDF文件合并与处理

```python
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os

def merge_pdfs(pdf_files, output_path):
    """合并多个PDF文件"""
    merger = PdfMerger()
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            merger.append(pdf_file)
            print(f"已添加：{pdf_file}")
    
    merger.write(output_path)
    merger.close()
    print(f"PDF合并完成：{output_path}")

def extract_pages(input_path, output_path, pages):
    """提取指定页面"""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page_num in pages:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    print(f"页面提取完成：{output_path}")

def add_watermark(input_path, watermark_path, output_path):
    """添加水印"""
    reader = PdfReader(input_path)
    watermark_reader = PdfReader(watermark_path)
    watermark_page = watermark_reader.pages[0]
    
    writer = PdfWriter()
    
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    print(f"水印添加完成：{output_path}")

# 使用示例
# merge_pdfs(['file1.pdf', 'file2.pdf'], 'merged.pdf')
# extract_pages('input.pdf', 'output.pdf', [0, 2, 4])  # 提取第1、3、5页
```

## 4. 邮件发送

### 4.1 使用smtplib发送邮件

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os

class EmailSender:
    def __init__(self, smtp_server, port, username, password):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
    
    def send_email(self, to_emails, subject, body, attachments=None, html=False):
        """发送邮件"""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
        msg['Subject'] = subject
        
        # 添加正文
        if html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 添加附件
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        attachment = MIMEApplication(f.read())
                        attachment.add_header(
                            'Content-Disposition', 
                            'attachment', 
                            filename=os.path.basename(file_path)
                        )
                        msg.attach(attachment)
        
        # 发送邮件
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
                print(f"邮件发送成功：{subject}")
                return True
        except Exception as e:
            print(f"邮件发送失败：{str(e)}")
            return False
    
    def send_html_email(self, to_emails, subject, html_content, attachments=None):
        """发送HTML格式邮件"""
        return self.send_email(to_emails, subject, html_content, attachments, html=True)
    
    def send_report_email(self, to_emails, report_path, report_name=None):
        """发送报告邮件"""
        if not report_name:
            report_name = os.path.basename(report_path)
        
        subject = f"报告发送：{report_name}"
        body = f"""
        <html>
        <body>
            <h2>报告通知</h2>
            <p>您好，</p>
            <p>请查收附件中的报告文件：<strong>{report_name}</strong></p>
            <p>如有问题，请及时联系。</p>
            <br>
            <p>此致</p>
            <p>数据分析部</p>
        </body>
        </html>
        """
        
        return self.send_html_email(to_emails, subject, body, [report_path])

# 使用示例
"""
email_sender = EmailSender(
    smtp_server='smtp.example.com',
    port=465,
    username='your_email@example.com',
    password='your_password'
)

# 发送简单邮件
email_sender.send_email(
    to_emails=['recipient@example.com'],
    subject='测试邮件',
    body='这是一封测试邮件。'
)

# 发送带附件的邮件
email_sender.send_report_email(
    to_emails=['manager@example.com'],
    report_path='sales_report.xlsx',
    report_name='销售报告'
)
"""
```

### 4.2 批量邮件发送

```python
import pandas as pd
import time
from datetime import datetime

class BatchEmailSender:
    def __init__(self, email_sender):
        self.sender = email_sender
        self.send_log = []
    
    def send_batch(self, recipients_file, subject_template, body_template, attachments=None):
        """批量发送邮件"""
        df = pd.read_excel(recipients_file)
        
        success_count = 0
        fail_count = 0
        
        for index, row in df.iterrows():
            name = row.get('姓名', '')
            email = row.get('邮箱', '')
            
            if not email:
                continue
            
            # 替换模板变量
            subject = subject_template.replace('{{姓名}}', name)
            body = body_template.replace('{{姓名}}', name)
            
            # 发送邮件
            result = self.sender.send_email(
                to_emails=[email],
                subject=subject,
                body=body,
                attachments=attachments
            )
            
            # 记录日志
            self.send_log.append({
                '时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '姓名': name,
                '邮箱': email,
                '主题': subject,
                '状态': '成功' if result else '失败'
            })
            
            if result:
                success_count += 1
            else:
                fail_count += 1
            
            # 避免发送过快
            time.sleep(1)
        
        # 保存发送日志
        log_df = pd.DataFrame(self.send_log)
        log_df.to_excel('email_send_log.xlsx', index=False)
        
        print(f"\n发送完成：成功 {success_count} 封，失败 {fail_count} 封")
        return success_count, fail_count

# 使用示例
"""
batch_sender = BatchEmailSender(email_sender)

subject_template = "{{姓名}}，您的月度报告已生成"
body_template = """
"""
<html>
<body>
    <h2>{{姓名}}，您好！</h2>
    <p>您的月度报告已经生成，请查收附件。</p>
    <p>如有疑问，请联系数据分析部。</p>
</body>
</html>
"""
"""

batch_sender.send_batch(
    recipients_file='recipients.xlsx',
    subject_template=subject_template,
    body_template=body_template,
    attachments=['monthly_report.pdf']
)
"""
```

## 5. 完整自动化办公流程

```python
import schedule
import time
from datetime import datetime

class OfficeAutomation:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, task_name, func, schedule_time):
        """添加定时任务"""
        self.tasks.append({
            'name': task_name,
            'func': func,
            'schedule': schedule_time
        })
        
        # 设置定时任务
        schedule.every().day.at(schedule_time).do(func)
        print(f"已添加任务：{task_name}，执行时间：{schedule_time}")
    
    def run(self):
        """运行自动化任务"""
        print("自动化办公系统启动...")
        print(f"已注册 {len(self.tasks)} 个任务")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

# 示例任务函数
def generate_daily_report():
    """生成每日报告"""
    print(f"[{datetime.now()}] 生成每日报告...")
    # 这里调用报告生成函数

def send_daily_email():
    """发送每日邮件"""
    print(f"[{datetime.now()}] 发送每日邮件...")
    # 这里调用邮件发送函数

def backup_files():
    """备份文件"""
    print(f"[{datetime.now()}] 备份文件...")
    # 这里调用文件备份函数

# 使用示例
"""
automation = OfficeAutomation()

automation.add_task('生成日报', generate_daily_report, '09:00')
automation.add_task('发送邮件', send_daily_email, '09:30')
automation.add_task('文件备份', backup_files, '18:00')

automation.run()
"""
```

## 最佳实践

### 1. 代码组织
- 将常用功能封装为类和函数
- 使用配置文件管理参数
- 实现错误处理和日志记录

### 2. 文件处理
- 始终使用`with`语句打开文件
- 处理大文件时使用流式读取
- 实现文件备份机制

### 3. 邮件安全
- 使用环境变量存储敏感信息
- 实现邮件发送频率限制
- 添加发送失败重试机制

### 4. 性能优化
- 使用多线程处理批量任务
- 实现任务队列管理
- 缓存常用数据

### 5. 测试与监控
- 编写单元测试
- 实现操作日志记录
- 设置异常报警机制

## 常见问题

### Q1: 如何处理Excel中的中文乱码？
```python
# 使用pandas读取时指定编码
df = pd.read_excel('file.xlsx', encoding='utf-8')

# 使用openpyxl时确保字体支持
from openpyxl.styles import Font
font = Font(name='微软雅黑')
```

### Q2: 如何发送大附件？
```python
# 压缩文件后发送
import zipfile

def compress_file(file_path):
    zip_path = file_path + '.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    return zip_path
```

### Q3: 如何处理PDF中的表格提取？
```python
# 使用tabula-py提取PDF表格
import tabula

tables = tabula.read_pdf('file.pdf', pages='all')
for i, table in enumerate(tables):
    table.to_csv(f'table_{i}.csv', index=False)
```

## 相关页面

- [[Python爬虫实战]] - 网络数据采集
- [[Python数据处理]] - 高级数据分析
- [[Python Web开发]] - Web应用开发
- [[Python机器学习实战]] - 机器学习应用

## 参考资源

- [openpyxl官方文档](https://openpyxl.readthedocs.io/)
- [python-docx官方文档](https://python-docx.readthedocs.io/)
- [ReportLab官方文档](https://www.reportlab.com/)
- [PyPDF2文档](https://pypdf2.readthedocs.io/)

---

*最后更新：2026年6月28日*