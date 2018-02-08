from django.core.management.base import BaseCommand
from doctree.models import Book, Chapter, Knowledge, FileUpload
import os, json, csv
import doctree.file_tool as ftool
from django.db.models.functions import Length, Upper

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('--word', nargs='+', dest='word',help='Needle word')
		parser.add_argument('--dir', dest='dir', help='To folder')
		# print(parser)

	def handle(self, *args, **options):
		# print(options)
		words = options['word']
		name = "_".join(words)
		folder = options['dir']
		csvFile = folder+"/"+name+"_tree.csv"

		words = options['word']
		lines = []
		for word in words:
			word = word.strip()
			lines.extend(self.wordlines(word))

		with open(csvFile, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerows(lines)
		
	def wordlines(self, word):
		knowledges = Knowledge.objects.filter(level=4, title__contains=word).order_by(Length('title'))

		klist = []
		selfie = None
		# tree = []
		for knowledge in knowledges:
			klist.append(knowledge)
			if knowledge.title == word and knowledge.status=='pass':
				selfie = knowledge

		# tree = []
		# for id,knowledge in klist:
		if selfie:
			depth = 0
			lines = []
		else :
			depth = 1
			lines = [[0, word]]
		tree = self.aggregate(klist, depth)

		for root in tree:
			lines.extend(self.tree2lines(root))

		if selfie:
			lines.extend(self.kg2lines(selfie, depth))

		# print(lines)

		return lines

	def aggregate(self, klist, depth=0):
		results = []

		while len(klist):
			needle = klist[0]
			needle.depth = depth
			klist.remove(needle)
			results.append(needle)
			self.findLeaf(needle, klist)

		for item in results:
			if len(item.leaf)>0:
				item.leaf = self.aggregate(item.leaf, item.depth+1)

		return results

	def findLeaf(self, needle, klist):
		needle.leaf = []
		for knowledge in klist:
			if self.isRoot(needle, knowledge):
				needle.leaf.append(knowledge)

		for leaf in needle.leaf:
			klist.remove(leaf)


		# if k2 is child of k1, return true
	def isRoot(self, k1, k2):
		return k1.title!=k2.title and k2.title.find(k1.title)>=0

	def tree2lines(self, tree):
		lines = []
		first = [tree.id]
		for x in range (0,tree.depth):
			first.append('')
		first.append(tree.title)
		lines.append(first)

		if len(tree.leaf)>0:
			for leaf in tree.leaf:
				lines.extend(self.tree2lines(leaf))

		return lines

	def kg2lines(self, knowledge, depth):
		lines = []
		knowledge.loadChildren(passon=True)
		first = [knowledge.id]
		for x in range (0, depth):
			first.append('')
		first.append(knowledge.title)
		content = knowledge.getFormatContent()
		if isinstance(content, list):
			lines.append(first)
			for item in content:
				line = [knowledge.id]
				for x in range (0, depth+1):
					line.append('')
				line.append(item)
				lines.append(line)
		elif content :
			content = content.replace('\n', '  ')
			first.append(content)
			lines.append(first)
		else :
			lines.append(first)

		if len(knowledge.children)>0:
			for child in knowledge.children:
				lines.extend(self.kg2lines(child, depth+1))

		return lines



