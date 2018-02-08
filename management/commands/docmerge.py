from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class Command(BaseCommand):

	# def add_arguments(self, parser):
	# 	parser.add_argument('level', nargs='+', type=int)
		# print(parser)

	def handle(self, *args, **options):
		lastId = 0
		length = 20

		books = Book.objects.all()
		# print(books)
		for book in books:
			chapters = book.chapter_set.values_list('id', flat=True)
			# print(chapters)
			lastId = 0
			knowledges = Knowledge.objects.filter(level=4, id__gt=lastId, chapter__in=chapters).order_by('id')[:length]
			while knowledges.count()>0:
				for knowledge in knowledges:
					self.merge(knowledge.title, chapters)
					if knowledge.id>lastId:
						lastId = knowledge.id
						print("lastId"+str(lastId))
				knowledges = Knowledge.objects.filter(level=4, id__gt=lastId, chapter__in=chapters).order_by('id')[:length]

	def merge(self, title, chapters):
		knowledges = Knowledge.objects.filter(level=4, title=title, chapter__in=chapters)
		
		childrenCount = {} #l4id : l5count

		for knowledge in knowledges:
			knowledge.loadChildren()
			childrenCount[knowledge.id] = knowledge.children.count()

		maxCount = 0
		maxKnowledge = 0

		for kid, children in childrenCount.items():
			if children>maxCount:
				maxCount = children
				maxKnowledge = kid

		# print(maxKnowledge)
		mertoTo = None
		try:
			mertoTo = Knowledge.objects.get(id=maxKnowledge)
		except Exception as e:
			mergeTo = None
		
		if mertoTo:
			for knowledge in knowledges:
				# print(knowledge)
				mertoTo.mergeFrom(knowledge)


