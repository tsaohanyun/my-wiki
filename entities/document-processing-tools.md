---
title: 文档处理工具
project: 通用知识
category: 工具
tags: [文档处理, Excel, PDF, Word, OfficeCLI]
created: 2026-05-27
updated: 2026-05-27
---

# 文档处理工具

## 概述

本页面汇总了Wiki知识库中涉及的各类文档处理工具和方法。

## Excel 电子表格处理

OfficeCLI 支持 .xlsx/.xls 格式的创建、读取、编辑和验证。

常用工具：
- **OfficeCLI**：`officecli create/view/get/query/set/add/remove` 等命令
- **Python pandas**：数据处理和分析
- **openpyxl**：Excel文件读写（仅在OfficeCLI不适用时使用）

## PDF 文档处理

- **pdftotext**：从PDF提取纯文本
- **pymupdf**：更高级的PDF解析
- **marker-pdf**：AI辅助PDF解析
- **Chrome headless**：HTML转PDF（`--print-to-pdf`）

图片型PDF（扫描件）无法提取文本，需OCR处理。

## Word 文档处理

- **OfficeCLI**：优先使用，支持.docx读写
- **python-docx**：.docx文件解析
- **catdoc**：旧版.doc文件文本提取
- **antiword**：另一种.doc提取工具

## 相关页面

- [[OfficeCLI]]
- [[PDF 文档处理]]
- [[Word 文档处理]]
