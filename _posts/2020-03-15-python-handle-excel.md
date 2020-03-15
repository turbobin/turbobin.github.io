---
layout:     post
title:      Python处理多个Excel
subtitle:   
date:       2020-03-15
author:     turbobin
header-img: 
catalog: true
category: 技术
tags: 
    - Python
---

碰到一个简单却有点复杂的需求，在此稍微记录一下。

有多个 Excel 文件，需要把里面的同一句文案的多个不同语言版本放在一起。

![](https://gitee.com/turbobin_cao/images/raw/master/20200311193044.png)

其中部分 Excel 内容是这样的：

![](https://gitee.com/turbobin_cao/images/raw/master/20200311193858.png)

每个 Excel 有多个子 table，且每个 table 格式都是一样的，每个语言版本的文案顺序是一样的。

下面使用 Python 开始处理 Excel：

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlrd
import os
import json

TRANSLATE_DICT = {}

def read_excel_content(languge, filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    workbook = xlrd.open_workbook(filename)
    tables = workbook.sheets()
    # print "tables:", len(tables)
    num = 300
    for table in tables:
        nrows = table.nrows
        ncols = table.ncols
        for i in range(1, nrows):
            languge_dict = {}
            zh = table.cell(i, 3).value
            la = table.cell(i, 4).value
            languge_dict["zh"] = zh.encode("utf-8")
            languge_dict[languge] = la.encode("utf-8")
            # print json.dumps(languge_dict, ensure_ascii=False)
            if num in TRANSLATE_DICT:
                TRANSLATE_DICT[num].update(languge_dict)
            else:
                TRANSLATE_DICT[num] = languge_dict

            num += 1

def read_excels():
    dic = {
        "fr": u"法语.xls",
        "bn": u"孟加拉语.xlsx",
        "pt": u"葡萄牙语.xls",
        "te": u"泰卢固语.xlsx",
        "ta": u"泰米尔语.xlsx",
        "th": u"泰语.xls",
        "es": u"西班牙语.xls",
        "hi": u"印地语.xlsx",
        "id": u"印尼语.xls",
        "en": u"英语.xlsx",
        "vi": u"越南语.xls"
    }
    for key, value in dic.items():
        read_excel_content(key, value)
    # print json.dumps(TRANSLATE_DICT, ensure_ascii=False, indent=4)
    with open("plan_content.json", "w") as f:
        json.dump(TRANSLATE_DICT, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    read_excels()
```

最后输出一个 json 文件：

```json
{
    "300": {
        "fr": "Plan de santé sportive (initial)", 
        "en": "Exercise Health Program (First Stage)", 
        "zh": "运动健康计划（初阶）", 
        "pt": "Plano de Saúde Esportiva (Estágio inicial)", 
        "vi": "Kế hoạch vận động lành mạnh (Giai đoạn sơ cấp)", 
        "bn": "স্বাস্থ্য কার্যক্রমের জন্য ব্যায়াম (প্রাথমিক)", 
        "hi": "स्वास्थ्य कार्यक्रम के लिए कसरत (प्राथमिक)", 
        "th": "แผนการออกกำลังกาย(ขั้นพื้นฐาน)", 
        "te": "ఆరోగ్య కార్యక్రమానికి వ్యాయామం (ప్రిలిమినరీ)", 
        "id": "Rencana Sehat Olahraga(Level awal)", 
        "es": "Plan de salud deportiva (nivel primario)", 
        "ta": "ஆரோக்கிய திட்டத்திற்கான உடற்பயிற்சி (தொடக்க நிலை)"
    }, 
    "301": {
        "fr": "Réchauffez-vous avant quatre minutes de course", 
        "en": "A four-minute warm-up before running", 
        "zh": "四分钟跑前热身", 
        "pt": "Aquecer-se antes de quatro minutos de corrida", 
        "vi": "Làm nóng cơ thể trước 4 phút chạy bộ", 
        "bn": "দৌড়ানোর আগে চার মিনিট শরীর গরম করা", 
        "hi": "दौड़ने से पहले चार मिनट वार्म-अप", 
        "th": "วอร์มอัพ4นาทีก่อนวิ่ง", 
        "te": "పరిగెత్తడానికి ముందు నాలుగు నిమిషాల వార్మ్ అప్ ", 
        "id": "Warm-up 4 menit sebelum berlari", 
        "es": "Calentamiento antes de correr por 4 minutos", 
        "ta": "ஓடுவதற்கு முன் நான்கு நிமிட நிமிடம் உடலை தயார் படுத்திக்கொள்ளுங்கள்"
    }, 
    ......
```