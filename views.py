from django.shortcuts import render,HttpResponse,redirect
from django.db.models import Count
from django.db.models.functions import Length, Upper
from doctree.models import Knowledge, Chapter, Book, LinkMissing
from doctree import models
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json,xlwt,docx


# Create your views here.
def index(request):
	return render(request, 'doctree/index.html')

def doctree(request, title):
	
	level = 4
	if title=="None":
		title = None
	knowledges = Knowledge.objects.filter(level=level, title=title)[:16]
	# print(knowledges)
	parents = []
	children = []

	for knowledge in knowledges:
		knowledge.loadAll()
		# knowledge.loadChildren()
		parents.append(knowledge)
	# 	children.append(knowledge.knowledge_set.order_by('title'))

	context = { 'parents':parents }

	return render(request, 'doctree/tree1.html', context)


def docmerge(request):
	
	action = request.POST.get('action')
	
	print(action)
	if action=="合并":
		merge_ids = request.POST.getlist('merge_ids[]')
		merge_to = request.POST.get('merge_to')
		merge_to = int(merge_to)

		if merge_ids and merge_to:
			parent = Knowledge.objects.get(id=merge_to)
			for merge_id in merge_ids:
				merge_id = int(merge_id)
				if merge_id != merge_to:
					merge_from= Knowledge.objects.get(id=merge_id)
					merge_from.loadChildren()
					for child in merge_from.children:
						child.parent = parent
						child.save()
					if merge_from.content:
						merge_from.title = merge_from.title+"_合并"
						merge_from.parent = parent
						merge_from.level = parent.level+1
						merge_from.save()
					else:
						merge_from.delete()
	elif action=="删除":
		merge_ids = request.POST.getlist('merge_ids[]')
		print(merge_ids)
		if merge_ids:
			for del_id in merge_ids:
				delKw = Knowledge.objects.get(id=del_id)
				delKw.deleteAll()

	goto = request.POST.get('prev_url')

	return HttpResponseRedirect(goto)

def knowledge(request, kid):
	knowledge = Knowledge.objects.get(id=kid)
	knowledge = knowledge.superParent()
	knowledge.loadAll()

	context = { 'knowledge' : knowledge , 'start' : knowledge.level }
	
	return render(request, 'doctree/knowledge.html', context)

def add_h4(request):
	books = models.Book.objects.all()
	if request.method=="POST":
		title = request.POST.get("title")
		category = request.POST.get("category")
		status = request.POST.get("status")
		content = request.POST.getlist("content")
		book = request.POST.get("book").split("-")[0].strip()
		summarized = request.POST.get("book").split("-")[1].strip()
		chapter=models.Book.objects.filter(title=book,summarized=summarized).first()
		print(chapter)
		if content[0].strip("'").strip(" "):
			if len(content) == 1:
				content = content[0].strip("'").strip(" ")
		else:
			content = None
		# models.Knowledge.objects.create(title=title, category=category, level=4, content=content, status=status,meta=None, chapter_id=chapter.id)
		return redirect("/kwlist")
	return render(request,"doctree/add_h4.html",{"books":books})
	
def add_knowledge(request,kid):
	if request.method=="POST":
		knowledge_obj = models.Knowledge.objects.filter(id=kid).first()
		level = knowledge_obj.level
		chapter_id = knowledge_obj.chapter_id
		title = request.POST.get("title")
		category = request.POST.get("category")
		status = request.POST.get("status")
		content = request.POST.getlist("content")
		if content[0].strip("'").strip(" "):
			if len(content)==1:
				content=content[0].strip("'").strip(" ")
		else:
			content = None
		models.Knowledge.objects.create(title=title, category=category, level=level + 1, content=content, status=status,
										meta=None, chapter_id=chapter_id, parent=knowledge_obj)
		if knowledge_obj.parent_id:
			return redirect("/knowledge/"+str(knowledge_obj.parent_id))
		else:
			return redirect("/knowledge/"+str(knowledge_obj.id))
	return render(request,"doctree/knowledge_add.html")

def edit_knowledge(request,kid):
	knowledge_obj = models.Knowledge.objects.filter(id=kid).first()
	contents = knowledge_obj.content
	if contents:
		if "[" and "]" and "'" in contents:
			contents = []
			for i in knowledge_obj.content.strip("[]").split("'"):
				i = i.strip(" ")
				if i and i != ","and i != "，":
					contents.append(i)
		elif "[" and "]" and '"' in contents:
			contents = []
			for i in knowledge_obj.content.strip("[]").split('"'):
				i = i.strip(" ")
				if i and i != ","and i != "，":
					contents.append(i)
		else:
			contents = [contents]
	if request.method == "POST":
		title = request.POST.get("title")
		category = request.POST.get("category")
		content = request.POST.getlist("content")
		if content:
			if len(content)==1 and content[0]!='"'and content[0]!="'":
				contentend=content[0].strip('"').strip("'")
			elif len(content)>1:
				contentend=[]
				for i in content:
					if i.strip("'").strip('"').strip(" "):
						contentend.append(i)
				if not contentend:
					contentend=None
			else:
				contentend=None
		else:
			contentend=None
		models.Knowledge.objects.filter(id=kid).update(title=title, category=category,content=contentend)
		if knowledge_obj.parent_id:
			if knowledge_obj.parent.parent_id:
				return redirect("/knowledge/"+str(knowledge_obj.parent.parent_id))
			else:
				return redirect("/knowledge/"+str(knowledge_obj.parent_id))
		else:
			return redirect("/knowledge/"+str(knowledge_obj.id))
	return render(request,"doctree/knowledge_edit.html",{"obj":knowledge_obj,"contents":contents})
	


def kwmerge(request):
	action = request.POST.get('action')
	if action=="从属":
		merge_ids = request.POST.getlist('merge_ids[]')
		merge_to = request.POST.get('merge_to')
		merge_to = int(merge_to)

		if merge_ids :
			if merge_to>0:
				parent = Knowledge.objects.get(id=merge_to)
				toLevel = parent.level+1
			elif merge_to==0 :
				parent = None
				toLevel = 4
			elif merge_to<0:
				toLevel = 4

			for merge_id in merge_ids:
				merge_id = int(merge_id)
				if merge_id != merge_to:
					merge_from= Knowledge.objects.get(id=merge_id)
					merge_from.parent = parent
					merge_from.setLevel(toLevel)
	elif action=="删除":
		merge_ids = request.POST.getlist('merge_ids[]')
		if merge_ids:
			for del_id in merge_ids:
				delKw = Knowledge.objects.get(id=del_id)
				delKw.deleteAll()
	elif action=="通过":
		merge_ids = request.POST.getlist('merge_ids[]')
		if merge_ids:
			for action_id in merge_ids:
				kw = Knowledge.objects.get(id=action_id)
				kw.setStatus("pass")
	elif action=="未通过":
		merge_ids = request.POST.getlist('merge_ids[]')
		if merge_ids:
			for action_id in merge_ids:
				kw = Knowledge.objects.get(id=action_id)
				kw.setStatus("reject")

	goto = request.POST.get('prev_url')

	return HttpResponseRedirect(goto)

def kwlist(request):
	
	klist = Knowledge.objects.filter(level=4)
	if request.GET.get('status'):
		status = request.GET.get('status')
		if status=="alone":
			klist = klist.filter(is_alone=True)
		else:
			klist = klist.filter(status=request.GET.get('status'))
	if request.GET.get('book_id'):
		book = Book.objects.get(id=request.GET.get('book_id'))
		book.checkFinished()
		chapter_ids = Chapter.objects.filter(book_id=request.GET.get('book_id')).values_list('id',flat=True)
		klist = klist.filter(chapter_id__in=chapter_ids)
	if request.GET.get('search'):
		klist = klist.filter(title__contains=request.GET.get('search'))

	klist = klist.order_by('-modified_at')
	paginator = Paginator(klist, 25) # Show 25 contacts per page
	page = request.GET.get('page')
	try:
	    knowledges = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    knowledges = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    knowledges = paginator.page(paginator.num_pages)

	for knowledge in knowledges:
	 	knowledge.loadBook()
	
	# print(knowledges.paginator.page_range)

	books = Book.objects.order_by('title','summarized', 'id')
	status = ["pending", "pass", "reject", "alone"]
	r = near_range(knowledges)
	search = request.GET.get('search')

	context = { 'knowledges' : knowledges, 'books' : books, 'status' : status, 'near_range' : r , 'search' : search}

	return render(request, 'doctree/kwlist.html', context)

def l5list(request):
	level = int(request.GET.get('level', 5))
	status = request.GET.get('status')
	
	if status:
		rlist = Knowledge.objects.filter(level=level, status=status).values('title').annotate(count=Count('id')).order_by('-count')
	else :
		rlist = Knowledge.objects.filter(level=level).values('title').annotate(count=Count('id')).order_by('-count')
	paginator = Paginator(rlist, 50)
	page = request.GET.get('page')

	try:
	    relationships = paginator.page(page)
	except PageNotAnInteger:
	    relationships = paginator.page(1)
	except EmptyPage:
	    relationships = paginator.page(paginator.num_pages)

	for rel in relationships:
		print(rel)

	r = near_range(relationships)

	context = { 'relationships' : relationships, 'near_range' : r, 'level':level }

	return render(request, 'doctree/l5list.html', context)

def show_relationship(request, title):
	klist = Knowledge.objects.filter(level=5, title = title).order_by('id')
	paginator = Paginator(klist, 25)
	page = request.GET.get('page')

	try:
	    knowledges = paginator.page(page)
	except PageNotAnInteger:
	    knowledges = paginator.page(1)
	except EmptyPage:
	    knowledges = paginator.page(paginator.num_pages)

	for knowledge in knowledges:
		knowledge.parent
		knowledge.loadAll()

	r = near_range(knowledges)

	context = { 'knowledges' : knowledges, 'near_range' : r, 'title' : title }

	return render(request, 'doctree/show_relationship.html', context)

def rejectlist(request):
	status=request.GET.get('status', 'reject')
	klist = Knowledge.objects.filter(status=status).order_by('chapter_id', '-level', 'parent_id', 'id')
	if request.GET.get('book_id'):
		ids = request.GET.get('book_id').split(',')
		chapter_ids = Chapter.objects.filter(book_id__in=ids).values_list('id',flat=True)
		klist = klist.filter(chapter_id__in=chapter_ids)
	paginator = Paginator(klist, 25)
	page = request.GET.get('page')

	try:
	    knowledges = paginator.page(page)
	except PageNotAnInteger:
	    knowledges = paginator.page(1)
	except EmptyPage:
	    knowledges = paginator.page(paginator.num_pages)

	r = near_range(knowledges)

	exist_ids = []

	results = []

	for knowledge in knowledges:
		if knowledge.id not in exist_ids:
			k = knowledge
			root_id = k.id
			result = []
			while k:
				root_id = k.id
				k.loadBook()
				result.insert(0, k)
				exist_ids.append(k.id)
				try:
					k=k.parent
				except Exception as e:
					k=None

			result.insert(0,root_id)
			results.append(result)

	context = { 'knowledges' : knowledges, 'near_range' : r, 'results' : results }

	return render(request, 'doctree/rejectlist.html', context)


def booklist(request):
	blist = Book.objects.order_by('title', 'summarized', 'id')
	paginator = Paginator(blist, 25)
	page = request.GET.get('page')

	try:
	    books = paginator.page(page)
	except PageNotAnInteger:
	    books = paginator.page(1)
	except EmptyPage:
	    books = paginator.page(paginator.num_pages)

	r = near_range(books)

	aggregates = []
	last = None
	for book in books:
		book.checkFinished()
		if last and last==book.title:
			aggregates[-1].append(book)
		else:
			last = book.title
			aggregates.append([book])
	
	context = { 'aggregates':aggregates , 'books':books, 'near_range' : r}
	
	return render(request, 'doctree/booklist.html', context)

def linkmissing(request):
	mlist = LinkMissing.objects
	status=request.GET.get('status')
	sort=request.GET.get('sort')
	if status:
		mlist = mlist.filter(status = status)
	if int(sort)<0:
		mlist = mlist.order_by(Length('word').desc())
	elif int(sort)>0:
		mlist = mlist.order_by(Length('word'))
	else:
		mlist = mlist.order_by('heading','source','link','id')

	paginator = Paginator(mlist, 50)
	page = request.GET.get('page')

	try:
	    links = paginator.page(page)
	except PageNotAnInteger:
	    links = paginator.page(1)
	except EmptyPage:
	    links = paginator.page(paginator.num_pages)

	r = near_range(links)

	for link in links:
		link.heading
		link.source
		link.link

	context = { 'links':links , 'near_range' : r}

	return render(request, 'doctree/linkmissing.html', context)

def near_range(pagination):
	half_range = 3
	current = pagination.number
	start = current-half_range
	if start<1:
		start = 1
	end = current+half_range
	if end>pagination.paginator.num_pages:
		end = pagination.paginator.num_pages

	return range(start, end+1)


def lawlist(request):
    if request.method == "GET":
        page_num = request.GET.get("page")
        law_query = models.Law.objects.all()
        if not page_num:
            page_num=1
        page_num = int(page_num)
        paginator = Paginator(law_query, 10)
        if paginator.num_pages > 10:
            if page_num - 5 < 1:
                pageRange = range(1, 11)
            elif page_num + 5 > paginator.num_pages:
                pageRange = range(page_num - 5, paginator.num_pages + 1)
            else:
                pageRange = range(page_num - 5, page_num + 5)
        else:
            pageRange = paginator.page_range

        law_query = paginator.page(page_num)
    else:
        return HttpResponse("ERROR!")

    return render(request,"doctree/lawlist.html",{"law_query":law_query,"num_pages":pageRange,"paginator":paginator,"page_num":page_num})

def law_title(request,law_id):
    if request.method == "GET":
        law = models.Law.objects.filter(id=law_id).first()
        ed_titles = models.Title.objects.filter(law_id=law_id,level="编")
        chapter_titles = models.Title.objects.filter(law_id=law_id,level="章")
        section_titles = models.Title.objects.filter(law_id=law_id,level="节")
        if not ed_titles and not chapter_titles and not section_titles:
            return redirect("/provision/"+str(law_id)+"/"+"provision"+"/"+"0")

    else:
        return HttpResponse("ERROR!")
    return render(request,"doctree/lawtitle.html",{"law":law,"ed_titles":ed_titles,"chapter_titles":chapter_titles,"section_titles":section_titles})

def provision_view(request,law_id,types,parent_id=None):
    if request.method == "GET":
        law = models.Law.objects.filter(id=law_id).first()
        if parent_id:
            now = models.Title.objects.filter(id=parent_id).first()
            now = "第"+str(now.self_num)+now.level+":"+now.name
        else:
            now = ""
        if types == "chapter":
            provisions = models.Provision.objects.filter(law_id=law_id,types="章条文",parent_id=parent_id)
            if not provisions:
                parent = models.Title.objects.filter(law_id=law_id,parent_id=parent_id,level="节")
                parents = []
                for i in parent:
                    parents.append(i.id)
                provisions = models.Provision.objects.filter(law_id=law_id,types="节条文",parent_id__in=parents)
        elif types == "section":
            provisions = models.Provision.objects.filter(law_id=law_id, types="节条文",parent_id=parent_id)
        elif types == "provision":
            provisions = models.Provision.objects.filter(law_id=law_id, types="条文")
    else:
        return HttpResponse("ERROR!")
    return render(request,"doctree/provision.html",{"law":law,"provisions":provisions,"now":now})
	
def export_file(request):
	if request.method == "POST":
		types = request.POST.get("type")

		def select_relative():
			checklist = request.POST.get("checklist")
			checklist = json.loads(checklist)
			checkid = []
			if checklist:
				for i in checklist:
					checkid.append(int(i.strip("\n").strip("\t")))
			h4, h5, h6 = {}, {}, {}
			for kid in checkid:
				obj = models.Knowledge.objects.filter(id=kid).first()
				if obj.parent:
					if obj.parent.parent:
						if obj.parent.parent.title not in h4:
							h4[obj.parent.parent.title] = {"content": obj.parent.parent.content,
														   "id": obj.parent.parent.id}
						if obj.parent.title not in h5:
							h5[obj.parent.title] = {"content": obj.parent.content, "id": obj.parent.id,
													"parent_id": obj.parent.parent.id}
						if obj.title not in h6:
							h6[obj.title] = {"content": obj.content, "id": obj.id, "parent_id": obj.parent.id}
					else:
						if obj.parent.title not in h4:
							h4[obj.parent.title] = {"content": obj.parent.content, "id": obj.parent.id}
						if obj.title not in h5:
							h5[obj.title] = {"content": obj.content, "id": obj.id, "parent_id": obj.parent.id}
						children = models.Knowledge.objects.filter(parent=obj)
						for child in children:
							if child.title not in h6:
								h6[child.title] = {"content": child.content, "id": child.id,
												   "parent_id": child.parent.id}
				else:
					if obj.title not in h4:
						h4[obj.title] = {"content": obj.content, "id": obj.id}
					children = models.Knowledge.objects.filter(parent=obj)
					for child in children:
						if child.title not in h5:
							h5[child.title] = {"content": child.content, "id": child.id,
											   "parent_id": child.parent.id}
						son = models.Knowledge.objects.filter(parent=child)
						for s in son:
							if s.title not in h6:
								h6[s.title] = {"content": s.content, "id": s.id, "parent_id": s.parent.id}
			return h4, h5, h6

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
			wbk.save("static/xls/" + file_name + ".xls")
			return "static/xls/" + file_name + ".xls"

		# wbk.save(r'doctree/management/xls/' + file_name + ".xls")
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
						p = doc.add_paragraph(style="Heading 9")
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
			doc.save("static/docx/" + file_name + ".docx")
			return "static/docx/" + file_name + ".docx"

		# doc.save(r'doctree/management/word/' + file_name + ".docx")
		def md_write(h4, h5, h6):
			for k, v in h4.items():
				file_name = k
				content = v.get("content")
			with open(r'static/markdown/' + file_name + ".md", "w", encoding="utf-8") as f:
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
			return "static/markdown/" + file_name + ".md"

		h4, h5, h6 = select_relative()
		if types == "excel":
			file_path = excel_write(h4, h5, h6)
		elif types == "word":
			file_path = word_write(h4, h5, h6)
		elif types == "markdown":
			file_path = md_write(h4, h5, h6)
		else:
			print("输出参数格式有误")

	return HttpResponse(file_path)


def book_chapter(request,bid):
	book = models.Book.objects.filter(id=bid).first()
	chapters=[]
	sections = []
	titles = []
	chapter=models.Chapter.objects.filter(book=book,parent=None)
	for c in chapter:
		chapters.append({"title":c.title,"id":c.id})
		section = models.Chapter.objects.filter(parent=c)
		for s in section:
			sections.append({"title":s.title,"pid":c.id,"id":s.id})
			title = models.Chapter.objects.filter(parent=s)
			for t in title:
				titles.append({"title":t.title,"pid":s.id})

	return render(request,"doctree/chapter.html",{"book":book,"chapters":chapters,"sections":sections,"titles":titles})