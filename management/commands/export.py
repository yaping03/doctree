from django.core.management.base import BaseCommand
from doctree import models
import os, json,docx,xlwt


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file', dest='file',nargs='+', type=str)
        parser.add_argument('--h5', dest='h5',nargs='+', type=str)
        parser.add_argument('--fmt',dest='fmt', nargs='+', type=str)
        print(parser)
    def handle(self,*args, **options):
        file = options['file'][0]
        filterlist=options['h5']
        filters = []
        for i in filterlist:
            if i.strip() and i.strip()!=",":
                for item in i.split(","):
                    if item.strip():
                        filters.append(item)
        print(filters)
        types=options['fmt'][0]
        def select_relative(line):
            h4, h5, h6 = {}, {}, {}
            title = line.strip("\n").strip()
            obj = models.Knowledge.objects.filter(title=title).first()
            if obj.title not in h4:
                h4[obj.title] = {"content": obj.content, "id": obj.id}
            if filters:
                for item in filters:
                    child = models.Knowledge.objects.filter(title=item, parent=obj).first()
                    if child:
                        if child.title not in h5:
                            h5[child.title] = {"content": child.content, "id": child.id, "parent_id": child.parent.id}
                            son = models.Knowledge.objects.filter(parent=child)
                            for s in son:
                                if s.title not in h6:
                                    h6[s.title] = {"content": s.content, "id": s.id, "parent_id": s.parent.id}
            else:
                fives = models.Knowledge.objects.filter(parent=obj)
                for child in fives:
                    if child.title not in h5:
                        h5[child.title] = {"content": child.content, "id": child.id, "parent_id": child.parent.id}
                        son = models.Knowledge.objects.filter(parent=child)
                        for s in son:
                            if s.title not in h6:
                                h6[s.title] = {"content": s.content, "id": s.id, "parent_id": s.parent.id}
            return h4,h5,h6

        def excel_write(h4, h5, h6):
            wbk = xlwt.Workbook()
            sheet = wbk.add_sheet('show_knowledge')
            sheet.write(0, 0, '标题')
            sheet.write(0, 1, 'H4内容、H5标题')
            sheet.write(0, 2, 'H5内容、H6标题')
            sheet.write(0, 3, 'H6内容')
            for k, v in h4.items():
                file_name = k
                sheet.write(1, 0, k)
                sheet.write(1, 1, v.get("content"))
            line = 1
            column = 1
            for title, swap in h5.items():
                line += 1
                sheet.write(line, column, title)
                if swap.get("content"):
                    if "[" and "]" in swap.get("content"):
                        contents = eval(swap.get("content"))
                        for content in contents:
                            sheet.write(line, column + 1, content)
                            line += 1
                    else:
                        sheet.write(line, column + 1, swap.get("content"))
                for k, v in h6.items():
                    if v.get("parent_id") == swap.get("id"):
                        line += 1
                        sheet.write(line, column + 1, k)
                        if v.get("content"):
                            if "[" and "]" in v.get("content"):
                                contents = eval(v.get("content"))
                                for content in contents:
                                    sheet.write(line, column + 2, content)
                                    line += 1
                            else:
                                sheet.write(line, column + 2, v.get("content"))
            wbk.save(r'doctree/management/xls/'+file_name + ".xls")

        def word_write(h4, h5, h6):
            doc = docx.Document()
            for k, v in h4.items():
                file_name = k
                p = doc.add_paragraph(style="Heading 1")
                w = p.add_run(k)
                w.font.bold = True
                p = doc.add_paragraph()
                w = p.add_run(v.get("content"))
            for title, swap in h5.items():
                p = doc.add_paragraph(style="Heading 3")
                w = p.add_run(title)
                w.font.bold = True
                if swap.get("content"):
                    if "[" and "]" in swap.get("content"):
                        contents = eval(swap.get("content"))
                        for content in contents:
                            p = doc.add_paragraph()
                            w = p.add_run(content)
                    else:
                        p = doc.add_paragraph()
                        w = p.add_run(swap.get("content"))
                for k, v in h6.items():
                    if v.get("parent_id") == swap.get("id"):
                        p = doc.add_paragraph(style="Heading 3")
                        w = p.add_run(k)
                        if v.get("content"):
                            if "[" and "]" in v.get("content"):
                                contents = eval(v.get("content"))
                                for content in contents:
                                    p = doc.add_paragraph()
                                    w = p.add_run(content)
                            else:
                                p = doc.add_paragraph()
                                w = p.add_run(v.get("content"))

            doc.save(r'doctree/management/word/'+file_name + ".docx")

        def md_write(h4, h5, h6):
            for k, v in h4.items():
                file_name = k
                content = v.get("content")
            with open(r'doctree/management/markdown/'+file_name + ".md", "w", encoding="utf-8") as f:
                f.writelines("#### " + file_name + "\n")
                if content:
                    f.writelines(content + "\n")
                for title, swap in h5.items():
                    f.writelines("##### " + title + "\n")
                    if swap.get("content"):
                        if "[" and "]" in swap.get("content"):
                            contents = eval(swap.get("content"))
                            for content in contents:
                                f.writelines("- " + content + "\n")
                        else:
                            f.writelines(swap.get("content") + "\n")
                    for k, v in h6.items():
                        if v.get("parent_id") == swap.get("id"):
                            f.writelines("###### " + k + "\n")
                            if v.get("content"):
                                if "[" and "]" in v.get("content"):
                                    contents = eval(v.get("content"))
                                    for content in contents:
                                        f.writelines("- " + content + "\n")
                                else:
                                    f.writelines(v.get("content") + "\n")
        with open(file,"r",encoding="utf-8")as f:
            for line in f:
                if line.strip().strip("\n"):
                    h4,h5,h6=select_relative(line)
                    if types == "excel":
                        excel_write(h4, h5, h6)
                    elif types == "word":
                        word_write(h4, h5, h6)
                    elif types == "markdown":
                        md_write(h4, h5, h6)
                    else:
                        print("输出参数格式有误")

