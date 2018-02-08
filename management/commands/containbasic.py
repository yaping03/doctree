from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json, csv
import doctree.file_tool as ftool

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('file', type=str)
		# print(parser)

	def handle(self, *args, **options):
		file = options['file']
		folder = os.path.dirname(file)
		name = os.path.basename(file)
		csvFile = folder+"/"+"scan.csv"
		lines = ftool.read_lines(file, should_strip=True)
		words = list(set(lines))
		words.remove('')
		words.sort(key=lambda word: len(word))
		# print(words)
		self.words = words.copy()
		words.reverse()
		self.reversedWords = words

		results = []
		knowledges = Knowledge.objects.filter(level=4)[:1]
		for knowledge in knowledges:
			info = self.scan(knowledge)
			results.append(info)

		# print(results)

		with open(csvFile, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerows(results)

	def scan(self, knowledge):
		# id, title, number of all contains, num of reverse & distinct, all contains of children, distinct of children, left
		title = knowledge.title
		if not title:
			title = ""

		title = title.strip()

		cnt = 0
		rcnt = 0
		for word in self.words:
			if title.find(word)>=0 and title!=word:
				cnt = cnt+1
				# print(word)

		for word in self.reversedWords:
			if title.find(word)>=0:
				rcnt = rcnt+1
				title = title.replace(word, '')


			

		knowledge.loadChildren()

		childrenCnt = 0
		childrenRCnt = 0

		for child in knowledge.children:
			count = self.scan(child)
			childrenCnt = count[2]+count[4]
			childrenRCnt = count[3]+count[5]

		result = [knowledge.id, knowledge.title, cnt, rcnt, childrenCnt, childrenRCnt]
		return result




