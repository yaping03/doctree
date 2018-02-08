import doctree.md_2_json as mdjson
from django.core.management.base import BaseCommand
import os, json

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('dir', nargs='+', type=str)

	def handle(self, *args, **options):
		# mdFolderPath = os.path.dirname(os.path.dirname(__file__))+"/MD"
		# jsonFolderPath = os.path.dirname(os.path.dirname(__file__))+"/JSON"

		mdFolderPath = options['dir'][0]
		jsonFolderPath = options['dir'][1]

		for mdFile in os.listdir(mdFolderPath):
			if self.isMarkdown(mdFile):
				mdPath = mdFolderPath+"/"+mdFile
				
				jsonFile = mdFile+".json"
				jsonPath = jsonFolderPath+"/"+jsonFile

				self.stdout.write("parsing: "+mdFile)

				mdjson.parse(mdPath, jsonPath)

		self.stdout.write("Parsing Finished")


		
	def isMarkdown(self, file):
		segs = file.split('.')
		return segs[-1].lower()=='md'