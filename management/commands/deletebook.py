from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('bookid', nargs='+', type=int)

		parser.add_argument('--keep', nargs='+', dest='keep', default=False,help='Keep the status')

		# parser.add_argument('status', nargs='+', type=str)
		# print(parser)

	def handle(self, *args, **options):
		
		bookids = options['bookid']
		keeps = options['keep']
		
		for bookid in bookids:
			book = Book.objects.get(id=bookid)
			self.stdout.write("deleting"+str(book))

			delbook = True

			chapters = book.chapter_set.order_by('id')
			for chapter in chapters:
				knowledges = chapter.knowledge_set.order_by('id')
				delchapter = True
				for knowledge in knowledges:
					if keeps and knowledge.status in keeps:
						delchapter = False
						delbook = False
					else:
						knowledge.delete()
				if delchapter:
					chapter.delete()

			if delbook:
				for upload in book.fileupload_set.order_by('id'):
					upload.delete()
				book.delete()




	


