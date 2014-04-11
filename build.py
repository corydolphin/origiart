'''
Placeholder for build script to minify and compress all static assets, and upload to S3 to improve performance
'''
from origiart import utils, app, config
import os
if __name__ == '__main__':

	print config.ProductionConfig.BUCKET
	root = 'origiart/static'
	for dr in os.listdir(root):
		dirPath = os.path.join(root,dr)
		if os.path.isdir(dirPath):
			for fil in os.listdir(dirPath):
				filPath = os.path.join(dirPath,fil)
				print filPath
				utils.uploadFile(file(filPath),filPath.replace('origiart/',''), metaData = '',bucket=config.ProductionConfig.BUCKET) #TEST
		else:
			utils.uploadFile(file(dirPath),dirPath.replace('origiart/',''), metaData = '',bucket=config.ProductionConfig.BUCKET)

	#def fn(x,y):
	#	print('%d of %d' % (x,y))

	#uploadFile(file('./bigfile'),'foo/bar', cb = fn) #TEST