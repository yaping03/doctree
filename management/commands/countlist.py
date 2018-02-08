from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os, json

class Command(BaseCommand):

	# def add_arguments(self, parser):
	# 	parser.add_argument('level', nargs='+', type=int)
		# print(parser)

	def handle(self, *args, **options):
		klist = Knowledge.objects.order_by('chapter_id','parent_id', 'id')
		paginator = Paginator(klist, 100)
		# print(paginator.page_range)
		total=0
		for p in paginator.page_range:
			page = paginator.page(p)
			cnt = self.findarray(page.object_list)
			total = total+cnt

		self.stdout.write("list count: "+str(total))

	def findarray(self, objects):
		count=0
		for knowledge in objects:
			try:
				listdata = json.loads(knowledge.content)
				count = count+len(listdata)
			except Exception as e:
				pass

		return count