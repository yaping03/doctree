from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json, csv, xlwt
import doctree.file_tool as ftool

class Command(BaseCommand):

	attributes = []
	core_words = []
	# words_only = False

	def add_arguments(self, parser):
		# parser.add_argument('--attr', dest="attr", type=str)
		# parser.add_argument('--words', dest="words", type=str)
		parser.add_argument('--dir', dest="dir", type=str)


	def handle(self, *args, **options):
		folder_path = os.path.dirname(os.path.dirname(__file__))+"/resources"
		attr_file = folder_path+"/attributes.csv"
		# words_file = options.get(words) 
		# if words_file:
		# 	words_only = True
		# else:
		words_file = folder_path+"/words.txt"
		dir = options['dir']
		xls_file = dir+"/matrix.xls"

		self.attributes = self.get_attribute(attr_file)
		self.core_words = self.get_words(words_file)

		book = xlwt.Workbook(encoding='utf-8', style_compression=0)

		for key, series in self.attributes.items():
			# if key == '分类':
			self.create_sheet(book, key, series)
			# break

		book.save(xls_file)

	def create_sheet(self, book, key, series):
		data = {}
		words = []

		print(series)

		for family in series:
			family_data = self.family_data(family, words)
			self.merge_dict(data, family_data)

		# print(data)

		headings = self.get_heading(series)
		rows = set(words)

		matrix = headings.copy()
		for cword in self.core_words:
			word_node = data.get(cword)
			if not word_node:
				row = [None for x in range(len(headings[1]))]
				row[0] = cword
			else:
				row = self.get_row(cword, word_node, series)

			matrix.append(row)
			try:
				rows.remove(cword)
			except Exception as e:
				pass
				
			

		# matrix.append([0 for x in range(len(headings))])
		# if not words_only:
		for word in rows:
			word_node = data.get(word)
			if word_node:
				row = self.get_row(word, word_node, series)
				matrix.append(row)
			
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

	def family_data(self, family, words):
		results = {}
		knowledges = Knowledge.objects.filter(level__in=[5,6], title__in=family)
		for knowledge in knowledges:
			# print(knowledge.id)
			parent = knowledge.superParent()
			if parent.title:
				parent_node = results.setdefault(parent.title.strip(), {})
				if knowledge:
					parent_node[knowledge.title] = "%s【%d】" % (knowledge.content, knowledge.id)
				words.append(parent.title)

		# print(results)
		return results

	def merge_dict(self, root, merge_from):
		for word, attributes in merge_from.items():
			word_node = root.setdefault(word, {})
			word_node.update(attributes)



	def get_attribute(self, dir):

		file = open(dir, 'r', encoding="utf-8-sig")
		reader = csv.reader(file)

		results = {}
		last_series = []
		for row in reader:

			if row[0]:
				last_series = []
				results[row[0]] = last_series

			del row[0]
			words = self.remove_idle(row)
			if len(words)>0:
				last_series.append(words)

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
		return results

	def get_heading(self, series):
		heading0 = [None, None]
		heading1 = ["词语", "总计"]
		for family in series:
			heading1.append("计数")
			heading1.extend(family)

			heading0.append(family[0])
			heading0.extend([None for x in range(len(family)-1)])
			heading0.append(None)

		return [heading0, heading1]

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




