from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json, csv, xlwt
import doctree.file_tool as ftool

class Command(BaseCommand):

	attributes = []
	core_words = []
	headings = ['词语', '计数']
	# words_only = False

	def add_arguments(self, parser):
		# parser.add_argument('--attr', dest="attr", type=str)
		# parser.add_argument('--words', dest="words", type=str)
		parser.add_argument('--dir', dest="dir", type=str)


	def handle(self, *args, **options):
		folder_path = os.path.dirname(os.path.dirname(__file__))+"/resources"
		attr_file = folder_path+"/attribute_lookup.csv"

		words_file = folder_path+"/words.txt"
		dir = options['dir']
		xls_file = dir+"/attributes_full.xls"

		self.attributes = self.get_attribute(attr_file)
		self.core_words = self.get_words(words_file)

		book = xlwt.Workbook(encoding='utf-8', style_compression=0)

		self.create_sheet(book, "统计")

		book.save(xls_file)

	def create_sheet(self, book, key):
		data = {}

		# print(data)

		# matrix = headings.copy()
		for cword in self.core_words:
			if cword:
				word_attributes = self.get_word_atribute(cword)
				data[cword] = word_attributes


		matrix = self.create_matrix(data)	
		# print(matrix)
		# print(matrix)

		# for word in rows:
		# 	word_node = data.get(word)
		# 	if word_node:
		# 		row = self.get_row(word, word_node, series)
		# 		matrix.append(row)
			
		sheet = book.add_sheet(key, cell_overwrite_ok=True)

		for i in list(range(len(matrix))):
			row = matrix[i]
			for j in list(range(len(row))):
				if row[j]:	
					sheet.write(i, j, row[j])
				else:
					sheet.write(i, j, ' ')

		# print(json.dumps(data, ensure_ascii=False))
		# ftool.write_json(data, os.path.dirname(os.path.dirname(__file__))+"/data/matrix.json")

	def create_matrix(self, data):
		matrix = [self.headings]
		for word, line_data in data.items():
			if word:
				line = self.create_line(word, line_data)
				matrix.append(line)
		return matrix

	def create_line(self, word, line_data):
		line = []
		count = 0
		for key in self.headings[2:]:
			value = line_data.get(key)
			line.append(value)
			if value:
				count +=1

		line.insert(0, count)
		line.insert(0, word)
		# print(line)
		return line

	def get_word_atribute(self, word):
		print(word)
		results = {}
		kwids = Knowledge.objects.filter(level=4, title=word).values_list('id',flat=True)

		for key, attributes in self.attributes.items():
			for attr in attributes:
				existed = self.get_word_existed(kwids, attr)
				if existed:
					results[key] = attr
					break

		return results


	def get_word_existed(self, word_ids, attr):
		existed = Knowledge.objects.filter(level=5, title=attr, parent_id__in=word_ids).count()
		if existed:
			return True
		else:
			return False
	
	def get_attribute(self, dir):

		file = open(dir, 'r', encoding="utf-8-sig")
		reader = csv.reader(file)

		results = {}
		last_series = []
		for row in reader:

			if row[0]:
				last_series = []
				results[row[0]] = last_series
				self.headings.append(row[0])

			del row[0]
			words = self.remove_idle(row)
			if len(words)>0:
				last_series.extend(words)

		return results

	def remove_idle(self, array):
		results = []

		for item in array:
			if item and not item.isdigit():
				results.append(item.strip())

		return results

	def get_words(self, dir):
		results = []
		with open(dir, encoding="utf-8-sig") as file:
			for word in file:
				results.append(word.strip())

		knowledges = Knowledge.objects.filter(level=4).values_list('title', flat=True)
		results = list(set(knowledges))
		return results

	def get_row(self, word, values_dict, series):
		row = [word, 0]
		total = 0
		for family in series:
			cnt = 0
			pos = len(row)
			row.append(0)
			for col in family:
				value = values_dict.get(col)
				row.append(value)
				if value:
					cnt = cnt+1
			row[pos] = cnt
			total = total+cnt

		row[1] = total
		return row




