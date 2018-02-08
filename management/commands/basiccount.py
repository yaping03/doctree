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
		csvFile = folder+"/"+name+".csv"

		lines = ftool.read_lines(file, should_strip=True)
		words = set(lines)

		statistic = {}

		for word in words:
			if len(word):
				count = { 'equal':0, 'start':0, 'end':0, 'contain':0 }

				count['equal'] = Knowledge.objects.filter(level=4, title=word).count()
				count['start'] = Knowledge.objects.filter(level=4, title__startswith=word).count()
				count['end'] = Knowledge.objects.filter(level=4, title__endswith=word).count()
				count['contain'] = Knowledge.objects.filter(level=4, title__icontains=word).count()

				statistic[word] = count

		# print(statistic)
		lines = self.toArray(statistic, ['equal', 'start', 'end', 'contain'])

		with open(csvFile, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerows(lines)


	def toArray(self, dict, titles):
		lines = []
		for word, count in dict.items():
			line = [word]
			for title in titles:
				line.append(count[title])
			lines.append(line)

		return lines