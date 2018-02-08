from django.core.management.base import BaseCommand
import json
import os
import doctree.models as models

class Command(BaseCommand):

    def handle(self, *args, **options):

        def create_law(law):
            """
             创建法律
            """
            meta = law.get("meta")
            publish_date = law.get("颁布")
            modify_date = law.get("修订")
            start_date = law.get("实施")
            end_date = law.get("终止")

            def handle_date(date=""):
                if date:
                    year = date.split("年")[0].strip(" ")
                    month = date.split("年")[1].split("月")[0].strip(" ")
                    day = date.split("年")[1].split("月")[1].split("日")[0].strip(" ")
                    return year + "-" + month + "-" + day

            if not modify_date:
                modify_date = publish_date
            if not start_date:
                start_date = modify_date
            obj = models.Law.objects.create(name=law["名称"], organization=law["组织"], short_name=law["简称"], type=law["类型"],
                                            meta=meta,
                                            publish_date=handle_date(publish_date), modify_date=handle_date(modify_date),
                                            start_date=handle_date(start_date), end_date=handle_date(end_date))
            return obj

        def create_title(obj, law):
            """
            章，节
            """
            creates = []
            for item in law["chapter"]:
                for k, v in item.items():
                    new = models.Title(law=obj, name=v['title'], level="章", self_num=v["chapter_num"])
                    creates.append(new)
                    # models.Title.objects.create(law=obj,name=v['title'],level="章",self_num=v["chapter_num"])
            models.Title.objects.bulk_create(creates)
            creates = []
            for item in law["section"]:
                for k, v in item.items():
                    parent = models.Title.objects.filter(law=obj, self_num=v["chapter_num"], level="章").first()
                    if parent:
                        new = models.Title(law=obj, name=v["title"], level="节", parent=parent,
                                           self_num=v["section_num"], parent_num=v["chapter_num"])
                    else:
                        new = models.Title(law=obj, name=v["title"], level="节", self_num=v["section_num"])
                    creates.append(new)
            models.Title.objects.bulk_create(creates)

        def create_provision(obj, law):
            creates = []
            for item in law["provision"]:
                for k, v in item.items():
                    parent = models.Title.objects.filter(law=obj, self_num=v["section_num"],
                                                         parent_num=v["chapter_num"], level="节").first()
                    if parent:
                        new = models.Provision(law=obj, content=v["content"], serial_number=k, types="节条文", parent=parent,
                                               num=v["num"])
                    else:
                        parent = models.Title.objects.filter(law=obj, self_num=v["chapter_num"], level="章").first()
                        if parent:
                            new = models.Provision(law=obj, content=v["content"], serial_number=k, types="章条文",
                                                   parent=parent,
                                                   num=v["num"])
                        else:
                            new = models.Provision(law=obj, content=v["content"], serial_number=k, types="条文", num=v["num"])

                    creates.append(new)
            models.Provision.objects.bulk_create(creates)

        # with open(r"D:\a_project\untitled\app01\law\中华人民共和国刑法（2015修正）.txt", "r", encoding="utf8")as f:


        def handle_start(i):
            i = i.replace("\u3000", " ")
            i = i.replace("\xa0", " ")
            if len(i.strip(" ")) > 6 and len(i.split(" ")) == 1 and i.strip(" ").startswith("第") and (
                    0 < i.strip("").find("条") < 7):
                tmp = i.split("条", maxsplit=1)
                i = tmp[0] + "条" + " " + tmp[1]
            elif len(i.strip(" ")) > 6 and len(i.split(" ")) == 1 and i.strip(" ").startswith("第") and (
                    0 < i.strip("").find("节") < 7):
                tmp = i.split("节", maxsplit=1)
                i = tmp[0] + "节" + " " + tmp[1]
            elif len(i.strip(" ")) > 5 and len(i.split(" ")) == 1 and i.strip(" ").startswith("第") and (
                    0 < i.strip("").find("章") < 7):
                tmp = i.split("章", maxsplit=1)
                i = tmp[0] + "章" + " " + tmp[1]
            return i

        def handle_chapter(i):
            chapter = i.strip(" ").split(" ")
            for item in chapter:
                if not item:
                    chapter.remove(item)
            return chapter

        # def handle_title(chapter,law):

        folder = os.path.dirname(os.path.dirname(__file__)) + "/law"
        for file in os.listdir(folder):
            if ".txt" in file:
                # print(file)
                file_path = folder+"/"+file
                with open(file_path,"r",encoding="utf8")as f:
                    law = {'chapter': [], "provision": [], "section": [], "ed": []}
                    num = 0    #条数
                    id = 0     #章数
                    section_num = 0     #节数
                    ed_num = 0          #编数
                    start = 0
                    meta = True
                    section = ""
                    title = ""
                    provision = ""

                    for i in f:
                        start += 1
                        i = handle_start(i)
                        data = i.split("::")
                        chapter = handle_chapter(i)
                        if "第一" in chapter[0]:
                            meta = False

                        '''
                        处理法律信息
                        '''
                        if start == 1 and len(data)==1:
                            law["名称"] = data[0].strip("\ufeff").strip(" ").strip("《").strip("》").strip("\n").strip("》")
                        elif len(data) == 2:
                            law[data[0].strip("\ufeff")] = data[1].strip(" ").strip("《").strip("》").strip("\n").strip("》")
                        elif meta and len(data)==1:
                            if law.get('meta'):
                                law["meta"] += i
                            else:
                                law["meta"] = i


                        #处理标题和内容信息

                        elif len(chapter)>1:
                            if chapter[0].strip(" ").startswith("第") and "章" in chapter[0]:      #处理章
                                section_num = 0
                                id += 1
                                if len(chapter)>2:
                                    for item in chapter[1:]:
                                        title += item.strip("\n")
                                else:
                                    title = chapter[1].strip("\n")
                                law["chapter"].append({chapter[0]: {"title":title,"chapter_num": id, "level": "章"}})

                            elif chapter[0].strip(" ").startswith("第") and "节" in chapter[0]:     #处理节
                                section_num += 1
                                if len(chapter)>2:
                                    for item in chapter[1:]:
                                        section += item.strip("\n")
                                else:
                                    section = chapter[1].strip("\n")
                                law["section"].append({chapter[0]: {"title": section,"chapter_num": id, "level": "节","section_num":section_num}})
                            elif "之一" in chapter[0]:
                                pass
                            elif chapter[0].strip(" ").startswith("第") and "条" in chapter[0] and (chapter[1].strip("\n")):      #处理条文
                                if len(chapter) > 1:
                                    num += 1
                                    if len(chapter) == 3:
                                        content = chapter[1] + chapter[2].strip("\n")
                                    else:
                                        content = chapter[1].strip("\n")
                                    provision = chapter[0].strip(" ")
                                    if len(provision)<10:
                                        law["provision"].append({provision: {"content": content, "type": "", "num": num,
                                                                            "chapter_num": id, "section_num": section_num}})


                            elif provision:                                                                                    #处理内容
                                law["provision"][num - 1][provision]["content"] += str(chapter).strip("[]").strip("\n")


                        elif start != 1 and chapter[0].strip("\n"):                                                           #处理丢失内容
                            law["provision"][num - 1][provision]["content"] += chapter[0].strip("\n")

                print(file)
                obj = create_law(law)
                create_title(obj,law)
                create_provision(obj,law)


        # # 编，章，节，条
        folder = os.path.dirname(os.path.dirname(__file__)) + "/ed"
        with open(folder + "/中华人民共和国刑法（2015修正）.txt", "r", encoding="utf8")as f:
            law = {'chapter': [], "provision": [], "section": [], "ed": []}
            num = 0  # 条数
            id = 0  # 章数
            section_num = 0  # 节数
            ed_num = 0  # 编数
            start = 0
            meta = True
            section = ""
            title = ""
            provision = ""
            for i in f:
                data = i.split("::")
                chapter = i.split("\u3000")
                # print(chapter)
                if len(data) == 2:
                    law[data[0].strip("\ufeff")] = data[1].strip("\n")
                elif len(chapter) > 1:
                    if "第" in chapter[0] and "编" in chapter[0]:
                        id = 0
                        ed_num += 1
                        law["ed"].append({chapter[0]: {"title": chapter[1].strip("\n"), "ed_num": ed_num, "level": "编"}})
                    elif "第" in chapter[0] and "章" in chapter[0]:
                        section_num = 0
                        id += 1
                        title = chapter[1].strip("\n")
                        law["chapter"].append({chapter[0]: {"title": title, "chapter_num": id, "level": "章", "ed_num": ed_num}})
                    elif "第" in chapter[0] and "节" in chapter[0]:
                        section_num += 1
                        section = chapter[0]
                        law["section"].append({section: {"title": chapter[1].strip("\n"), "chapter_num": id, "level": "节",
                                                         "section_num": section_num, "ed_num": ed_num}})
                    elif "第" in chapter[0] and "条" in chapter[0]:
                        num += 1
                        provision = chapter[0]
                        law["provision"].append({provision: {"content": chapter[1].strip("\n"), "type": "", "num": num,
                                                             "chapter_num": id, "section_num": section_num, "ed_num": ed_num}})

                else:
                    law["provision"][num - 1][provision]["content"] += chapter[0].strip("\n").strip("\u3000\u3000")

        meta = law.get("meta")
        publish_date = law.get("颁布")
        modify_date = law.get("修订")
        start_date = law.get("实施")
        end_date = law.get("终止")

        def handle_date(date=""):
            if date:
                year = date.split("年")[0].strip(" ")
                month = date.split("年")[1].split("月")[0].strip(" ")
                day = date.split("年")[1].split("月")[1].split("日")[0].strip(" ")
                return year + "-" + month + "-" + day

        if not modify_date:
            modify_date = publish_date
        if not start_date:
            start_date = modify_date
        obj = models.Law.objects.create(name=law["名称"], organization=law["组织"], short_name=law["简称"], type=law["类型"],
                                        meta=meta,
                                        publish_date=handle_date(publish_date), modify_date=handle_date(modify_date),
                                        start_date=handle_date(start_date), end_date=handle_date(end_date))





            # """
            #    编，章，节，条
            # """
        for item in law["ed"]:
            for k, v in item.items():
                models.Title.objects.create(law=obj, name=v['title'], level="编", self_num=v["ed_num"])
        for item in law["chapter"]:
            for k, v in item.items():
                parent = models.Title.objects.filter(law=obj, self_num=v["ed_num"], level="编").first()
                if parent:
                    models.Title.objects.create(law=obj, name=v['title'], level="章", self_num=v["chapter_num"],
                                                parent_num=v["ed_num"], parent=parent)
                else:
                    models.Title.objects.create(law=obj, name=v['title'], level="章", self_num=v["chapter_num"])
        for item in law["section"]:
            for k, v in item.items():
                parent = models.Title.objects.filter(law=obj, self_num=v["chapter_num"], parent_num=v["ed_num"],
                                                     level="章").first()
                if parent:
                    models.Title.objects.create(law=obj, name=v["title"], level="节", parent=parent,
                                                self_num=v["section_num"], parent_num=v["chapter_num"])
                else:
                    models.Title.objects.create(law=obj, name=v["title"], level="节", self_num=v["section_num"])

        ed = 0
        for item in law["provision"]:
            for k, v in item.items():
                parent_ed = models.Title.objects.filter(law=obj, self_num=v["chapter_num"], parent_num=v["ed_num"],
                                                        level="章").first()
                parent = models.Title.objects.filter(self_num=v["section_num"], parent_num=v["chapter_num"], level="节",
                                                     parent=parent_ed).first()
                if parent:
                    models.Provision.objects.create(law=obj, content=v["content"], serial_number=k, types="节条文",
                                                    parent=parent, num=v["num"])
                else:
                    parent = models.Title.objects.filter(law=obj, self_num=v["chapter_num"], parent_num=v["ed_num"],
                                                         level="章").first()
                    if parent:
                        models.Provision.objects.create(law=obj, content=v["content"], serial_number=k, types="章条文",
                                                        parent=parent, num=v["num"])
                    else:
                        parent = models.Title.objects.filter(law=obj, self_num=v["ed_num"], level="编").first()
                        if parent:
                            models.Provision.objects.create(law=obj, content=v["content"], serial_number=k, types="编条文",
                                                            parent=parent, num=v["num"])



