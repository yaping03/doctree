from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json, csv, xlwt
import doctree.file_tool as ftool

class Command(BaseCommand):

	headings = []
	modify_model = False
	statistics = []
	cols = []
	default_key = '同义词'

	def add_arguments(self, parser):
		# parser.add_argument('--attr', dest="attr", type=str)
		# parser.add_argument('--words', dest="words", type=str)
		parser.add_argument('--dir', dest="dir", type=str)
		parser.add_argument('--modify', dest="modify", type=bool)



	def handle(self, *args, **options):
		folder_path = os.path.dirname(os.path.dirname(__file__))+"/resources"
		words_file = folder_path+"/nearwords.csv"
		self.modify_model = options['modify']
		dir = options['dir']
		xls_file = dir+"/near_words.xls"

		file = open(words_file, 'r', encoding="utf-8-sig")
		reader = csv.reader(file)
		no = 0

		results = {}

		for row in reader:
			if no<1:
				self.headings = row
				no +=1
			else:
				series = self.get_series(row)
				key = row[0].strip()
				existed = results.get(key)
				if existed:
					results[key] = self.merge_dict(existed, series)
				else :
					results[key] = series

		self.strip_nearwords(results)
		self.merge_nearwords(results)
		matrix = self.matrix_nearwords(results)

		book = xlwt.Workbook(encoding='utf-8', style_compression=0)
		self.create_sheet(book, 'matrix', matrix)

		book.save(xls_file)

	def matrix_nearwords(self, word_dict):
		for words in word_dict.values():
			self.cols.extend(words.keys())
		self.cols = list(set(self.cols))
		self.cols.insert(0, '')

		matrix = [self.cols]
		join = "、"
		r = range(1, len(self.cols))
		for key, words in word_dict.items():
			row = [key]
			for i in r:
				col = self.cols[i]
				content = words.get(col)
				value = None
				if content:
					value = join.join(content)

				row.append(value)
			matrix.append(row)

		return matrix

	def merge_nearwords(self, word_dict):
		keys = list(word_dict.keys())
		reverse = list(range(len(word_dict)))
		reverse.reverse()

		for idx2 in reverse:
			key2 = keys[idx2]
			series2 = word_dict[key2]
			for idx1 in range(idx2):
				key1 = keys[idx1]
				series1 = word_dict[key1]

				overlap = self.existed(series1, series2)
				if overlap:
					self.merge_dict(series2, {self.default_key: [key2]})
					self.merge_dict(series1, series2)
					del word_dict[key2]
					break
		


	def strip_nearwords(self, word_dict):
		for key in list(word_dict.keys()):  
			if not word_dict[key] or len(word_dict[key]) is 0:
				del word_dict[key]


	def get_series(self, row):
		word = row[0]
		series = {}
		for i in range(1, len(row)):
			content = row[i].strip(' ')
			key = self.headings[i]
			if content:
				words = self.get_words(content, key)
				family = series.setdefault(key, [])
				family.extend(words)
				family = set(family)

		return series



	def get_words(self, content, key=None):
		words = content
		results = [content]
		if content.endswith('】'):
			sp = content.split('【')
			words = sp[0]
			kid = sp[-1][:-1]
			if self.modify_model and key:
				try:
					knowledge = Knowledge.objects.get(id=kid)
					knowledge.title = key
					knowledge.save()
				except Exception as e:
					print("missing knowledge id="+kid)
				
		try:
			results= json.loads(words)
		except Exception as e:
			results =  words.split('、')

		return results

	def merge_dict(self, merge_to, merge_from):
		for key, words in merge_from.items():
			if merge_to.__contains__(key):
				existed = merge_to[key]
				existed.extend(list(words))
				merge_to[key] = list(set(existed))
			else:
				merge_to[key] = list(set(words))

	def existed(self, series1, series2):
		list1 = self.flat(series1)
		list2 = self.flat(series2)
		result = False
		for word in list2:
			try:
				list1.index(word)
				result = True
				break
			except Exception as e:
				pass

		return result

	def flat(sef, series):
		results = []
		for words in series.values():
			results.extend(words)

		return results

	def create_sheet(self, book, name, matrix):
		sheet = book.add_sheet(name, cell_overwrite_ok=True)

		for i in range(len(matrix)):
			row = matrix[i]
			for j in range(len(row)):
				sheet.write(i, j, row[j])
