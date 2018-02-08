from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('--from', nargs='+', dest='from',help='From books')
		parser.add_argument('--to', dest='to', help='To book')

		# parser.add_argument('status', nargs='+', type=str)
		# print(parser)

	def handle(self, *args, **options):
		print(options)
		fromIds = options['from']
		toId = options['to']
		if not fromIds or not toId:
			self.stdout.write("Please input from books and to book!")
		else:
			toBook = Book.objects.get(id=toId)
			for fromId in fromIds:
				fromBook = Book.objects.get(id=fromId)
				toBook.mergeBook(fromBook)
