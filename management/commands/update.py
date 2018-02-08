from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('dir', nargs='+', type=str)
		# print(parser)

	def handle(self, *args, **options):
		folderPath = options['dir'][0]
		files = os.listdir(folderPath)
		
		for file in files:
			willUpload = True
			if self.isJson(file):
				uploaded = FileUpload.objects.filter(title=file).order_by('-book_id','-created_at')
				book = None
				if uploaded.count():
					uploaded = uploaded[0]
				else:
					upload = None
				if uploaded:
					try:
						book = uploaded.book
					except Exception as e:
						book = None
						uploaded.book = None
						uploaded.save()

					if uploaded and book :
						message = input("文件：【"+file+"】已在下列时间上传：\n"+str(uploaded.created_at)+"\n是否重复上传 (yes/no?)")
						if message=="yes":
							willUpload = True
						else :
							willUpload = False
				
				if willUpload :
					uploading = FileUpload(title = file)
					uploading.book = book
					uploading.save()



					filePath = folderPath+"/"+file
					self.stdout.write("uploading: "+file)
					data = self.loadJSON(filePath)
					book = self.loadBook(data, uploading)
					level1 = self.loadIndex(data, 1, book, None)

	def isJson(self, file):
		segs = file.split('.')
		return segs[-1].lower()=='json'

	def loadJSON(self, filePath):
		json_data = open(filePath).read()
		data = json.loads(json_data)
		return data

	def loadBook(self, bookDict, upload=None):
		if upload and upload.book:
			book = upload.book
		else :
			bookInfo = bookDict['基本信息']
			book = Book()
			try:
				book.title = bookInfo.get('书名')
				book.summarized = bookInfo.get('整理者')
				book.author = bookInfo.get('作者')
			except:
				self.stderr.write("ERROR")

			book.save()
			upload.book = book
			upload.save()

		return book
		# print(book)

		#载入下级目录
		#levelDict:当前level的父级dictionary
	def loadIndex(self, levelDict, level, book, parent):
		result = True

		chapters = self.getChapters(levelDict, level)

		if chapters:
			for chapterDict in chapters:
				self.loadChapter(chapterDict, level, book, parent)
		else:
			result = False

		return result


		#载入当前目录
		#levelItem:当前level的dictionary	
	def loadChapter(self, levelItem, level, book, parent):
		hasNext = False

		chapter = Chapter()
		chapter.title = levelItem.get('title')
		try:
			chapter.book = book
			chapter.parent = parent
			chapter.level = level
			chapter.save()
		except:
			print("ERROR: "+chapter)

		hasNext = False

		if level<3:
			hasNext = self.loadIndex(levelItem, level+1, book, chapter)
		
		if (not hasNext):
			nextKnowledges = self.getKnowledges(levelItem, 4)
			if nextKnowledges:
				for k in nextKnowledges:
					self.loadKnowledge(k, 4, chapter, None)


	def loadKnowledge(self, levelItem, level, chapter, parent):

		knowledge = None
		if level==4:
			existed = Knowledge.objects.filter(level=4, title=levelItem.get('title'), status='pass').order_by('id')
			if existed:
				knowledge = existed[0]
				self.stdout.write("update: "+str(knowledge))
		elif level==5:
			existed = Knowledge.objects.filter(level=5, title=levelItem.get('title'), parent_id=parent.id).order_by('id')
			if existed:
				for k in existed:
					k.deleteAll()

		if not knowledge:
			knowledge = Knowledge()
			knowledge.title = levelItem.get('title')
			knowledge.category = levelItem.get('type')
			knowledge.level = level
			knowledge.chapter = chapter
			knowledge.parent = parent

		content = levelItem.get('content')
		if content:
			knowledge.content = content
		else:
			content = levelItem.get('list')
			if content:
				knowledge.content = json.dumps(content, ensure_ascii=False)

		knowledge.status = 'pass'
		knowledge.save()

		nextKnowledges = self.getKnowledges(levelItem, level+1)
		if nextKnowledges:
			for k in nextKnowledges:
				self.loadKnowledge(k, level+1, chapter, knowledge)


	def getChapters(self, levelDict, level):
		result = None

		if level<=3:
			levelKey = "level"+str(level)
			chapters = levelDict.get(levelKey)
			if chapters:
				result = chapters

		return result

	def getKnowledges(self, levelDict, level):
		result = None
		levelKey = "level"+str(level)
		knowledges = levelDict.get(levelKey)
		if knowledges:
			result = knowledges

		return result


