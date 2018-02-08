from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload, LinkMissing
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json, csv

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('dir', type=str)


	def handle(self, *args, **options):
		folder = options['dir']
		klist = Knowledge.objects.filter(content__startswith="[", content__endswith="]").all()
		csvFile = folder+"/"+"linking.csv"

		lines = []
		for knowledge in klist:
			linking = self.checkmissing(knowledge)
			lines.extend(linking)

		# lines = [["a"],["ab"], ["abc"], ["abcde"], ["abcd"]]
		lines.sort(key=lambda line: len(line[1]))

		# print(lines)

		with open(csvFile, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerows(lines)

	def checkmissing(self, knowledge):
		results = []
		try:
			linkList = json.loads(knowledge.content)
			for word in linkList:
				word = word.strip()
				cnt = Knowledge.objects.filter(title=word, level=4).count()
				if cnt<=0:
					results.append([knowledge.id, word, cnt])
		except Exception as e:
			self.stdout.write("Not List : "+str(knowledge) + knowledge.content)

		return results


'''
	def handle(self, *args, **options):
		folder = options['dir']
		klist = Knowledge.objects.filter(content__startswith="[", content__endswith="]").order_by('chapter_id','parent_id', 'id')
		paginator = Paginator(klist, 100)
		# print(paginator.page_range)

		for p in paginator.page_range:
			pagelist = paginator.page(p)
			for knowledge in pagelist:
				self.checkmissing(knowledge)

		# self.stdout.write("list count: "+str(total))

	def checkmissing(self, knowledge):
		try:
			linkList = json.loads(knowledge.content)
			for word in linkList:
				word = word.strip()
				existed = LinkMissing.objects.filter(source=knowledge.id, word=word)
				if existed.count():
					for link in existed:
						hasLink = self.checklink(link)
						if not hasLink:
							self.findtarget(word, knowledge, link)
				else:
					self.findtarget(word, knowledge)
		except Exception as e:
			self.stdout.write("Not List : "+str(knowledge) + knowledge.content)

	def checklink(self, link):
		result = False
		try:
			link.source
			link.link
			if link.source and link.link:
				result = True
		except Exception as e:
			result = False

		if not result:
			self.stdout.write("Delete : "+str(link.id) + link.word)
			link.delete()

		return result


	def findtarget(self, word, source, link=None):
		targets = Knowledge.objects.filter(title=word, level=4).order_by('status', 'id')
		if targets.count():
			for target in targets:
				if not link:
					link = LinkMissing()
				link.heading = source.superParent()
				link.source = source
				link.link = target
				link.word=word
				link.status="pass"
				link.save()
		else:
			LinkMissing.objects.create(heading = source.superParent(), source = source, word=word)


'''	
	


