from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os, json

class Command(BaseCommand):

	def handle(self, *args, **options):
		max_level = Knowledge.objects.order_by("-level").values_list('level', flat=True)[0]
		# print(max_level)
		level = max_level
		while level >= 0:	
			if level > 3:
				count = self.deleteKnowledge(level)
				self.stdout.write("deleted at level "+str(level)+", count: "+str(count))
			elif level >0 :
				count = self.deleteChapter(level)
				self.stdout.write("deleted at level "+str(level)+", count: "+str(count))
			else :
				count = self.deleteBook()
				self.stdout.write("deleted at level "+str(level)+", count: "+str(count))

			level = level-1

		self.stdout.write("finished deleting")

	def deleteKnowledge(self, level):
		klist = Knowledge.objects.filter(level = level, status="pending").order_by('chapter_id','parent_id', 'id')
		paginator = Paginator(klist, 100)
		# print(paginator.page_range)
		total = 0
		for p in reversed(paginator.page_range):
			page = paginator.page(p)
			for knowledge in page.object_list:
				if not knowledge.hasChildren():
					# print(knowledge.id)
					# knowledge.status="deleted"
					knowledge.delete()
					total = total +1
		# Knowledge.objects.filter(level = level, status="deleted").delete()
		return total

	def deleteChapter(self, level):
		klist = Chapter.objects.filter(level = level).order_by('book_id','parent_id', 'id')
		paginator = Paginator(klist, 100)
		# print(paginator.page_range)
		total = 0
		for p in reversed(paginator.page_range):
			page = paginator.page(p)
			for chapter in page.object_list:
				if not chapter.hasChildren():
					chapter.delete()
					total = total +1
		return total
	def deleteBook(self):
		klist = Book.objects.order_by('id')
		paginator = Paginator(klist, 100)
		# print(paginator.page_range)
		total = 0
		for p in reversed(paginator.page_range):
			page = paginator.page(p)
			for book in page.object_list:
				if not book.hasChildren():
					book.delete()
					total = total +1
		return total
