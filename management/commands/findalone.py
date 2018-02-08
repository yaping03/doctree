from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('level', nargs='+', type=int)
		# print(parser)

	def handle(self, *args, **options):
		level = options['level'][0]

		klist = Knowledge.objects.filter(level = level).order_by('chapter_id','parent_id', 'id')
		paginator = Paginator(klist, 100)
		# print(paginator.page_range)
		for p in paginator.page_range:
			page = paginator.page(p)
			self.findparent(page.object_list)

	def findparent(self, objects):
		for knowledge in objects:
			try:
				knowledge.parent
			except Exception as e:
				knowledge.is_alone=True
				knowledge.save()
				# print(knowledge)

