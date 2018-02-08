from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class Command(BaseCommand):

	def handle(self, *args, **options):
		lastId = 0
		length = 20

		knowledges = Knowledge.objects.filter(level=4, id__gt=lastId, content__isnull=False).order_by('id')[:length]
		while knowledges.count()>0:
			for knowledge in knowledges:
				self.transfer(knowledge)
				if knowledge.id>lastId:
					lastId = knowledge.id
					print("lastId"+str(lastId))
			knowledges = Knowledge.objects.filter(level=4, id__gt=lastId, content__isnull=False).order_by('id')[:length]

	# def transfer(self, level4):
	# 	level4


