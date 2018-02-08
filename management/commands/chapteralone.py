from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class Command(BaseCommand):

	# def add_arguments(self, parser):
	# 	parser.add_argument('level', nargs='+', type=int)
		# print(parser)

	def handle(self, *args, **options):
		klist = Chapter.objects.order_by('book_id','parent_id', 'id')
		paginator = Paginator(klist, 100)
		# print(paginator.page_range)
		for p in paginator.page_range:
			page = paginator.page(p)
			self.findparent(page.object_list)

	def findparent(self, objects):
		for chapter in objects:
			try:
				if chapter.level>1 :
					chapter.parent
				else :
					chapter.book
			except Exception as e:
				# knowledge.status="alone"
				# knowledge.save()
				print(chapter)

