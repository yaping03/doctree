from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json, xlwt

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('dir', nargs='+', type=str)
		# parser.add_argument('json_dir', dest='json_dir', type=str)
		# parser.add_argument('to', dest='to', type=str)
		# print(parser)

	def handle(self, *args, **options):
		# print(options)
		json_folder = options['dir'][0]
		to_folder = options['dir'][1]
		to_file = to_folder+"/quotation.xls"

		headings = ['人物', '关于', '名言']
		matrix = [headings]
		
		for file in os.listdir(json_folder):
			if self.isJson(file):
				file_path = json_folder+"/"+file
				data = self.loadJSON(file_path)
				level4s = data['level1'][0]['level2'][0]['level3'][0]['level4']

				lines = self.get_quotations(level4s)

				matrix.extend(lines)

		book = xlwt.Workbook(encoding='utf-8', style_compression=0)
		self.create_sheet(book, '名言', matrix)

		book.save(to_file)



	def get_quotations(self, level4s):
		results = []
		# print(level4s)
		for l4 in level4s:
			# try:
			person = l4.get('title')
			# except Exception as e:
			# 	print(l4)
			# 	continue
			
			
			l4_content = l4.get('content')
			if not l4_content:
				l4_content = l4.get('list')
			if l4_content:
				lines = self.get_content(l4_content, person, None)
				results.extend(lines)
			level5s = l4.get('level5')
			if not level5s:
				continue
			for l5 in level5s:
				word = l5['title']
				l5_content = l5.get('content')
				if not l5_content:
					l5_content = l5.get('list')
				lines = self.get_content(l5_content, person, word)
				results.extend(lines)

		return results


	def get_content(self, contents, person, word):
		results = []
		sentences = []
		if isinstance(contents, list):
			sentences = contents
		else:
			sentences = [contents]

		for sentence in sentences:
			sentence = sentence.strip(" ")
			sentence = sentence.strip("“”‘’\"")
			line = [person, word, sentence]
			results.append(line)

		return results
		
	def isJson(self, file):
		segs = file.split('.')
		return segs[-1].lower()=='json'

	def loadJSON(self, filePath):
		json_data = open(filePath).read()
		data = json.loads(json_data)
		return data

	def create_sheet(self, book, name, matrix):
		sheet = book.add_sheet(name, cell_overwrite_ok=True)

		for i in range(len(matrix)):
			row = matrix[i]
			for j in range(len(row)):
				sheet.write(i, j, row[j])

