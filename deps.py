"""Download and extract dependencies.
"""

import os
import re
import urllib
import fnmatch
import shutil
import zipfile

PIL_DOWNLOAD_URL = "http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe"

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DEPS_DIR = os.path.join(ROOT_DIR, "deps")
PLUGIN_DIR = os.path.join(ROOT_DIR, "addon", "globalPlugins", "imageDescriber")

depFiles = set()

def downloadDeps():
	try:
		os.mkdir(DEPS_DIR)
	except OSError:
		pass

	urls = [PIL_DOWNLOAD_URL]

	print("Downloading dependencies")
	for url in urls:
		fn = os.path.basename(url)
		localPath = os.path.join(DEPS_DIR, fn)
		depFiles.add(localPath)
		if os.path.isfile(localPath):
			print("%s already downloaded" % fn)
			continue
		print "Downloading %s" % fn
		# Download to a temporary path in case the download aborts.
		tempPath = localPath + ".tmp"
		urllib.urlretrieve(url, tempPath)
		os.rename(tempPath, localPath)

def extractPil():
	pilDir = os.path.join(PLUGIN_DIR, "PIL")
	print "Extracting PIL"
	shutil.rmtree(pilDir, ignore_errors=True)
	try:
		os.mkdir(pilDir)
	except OSError:
		pass

	with zipfile.ZipFile(os.path.join(DEPS_DIR, os.path.basename(PIL_DOWNLOAD_URL))) as zf:
		for realFn in zf.namelist():
			if not realFn.startswith("PLATLIB/PIL/") or realFn.endswith("/"):
				continue
			fn = os.path.basename(realFn)
			extractFn = os.path.join(pilDir, fn)
			with zf.open(realFn) as inf, file(extractFn, "wb") as outf:
				shutil.copyfileobj(inf, outf)

def main():
	downloadDeps()
	extractPil()

if __name__ == "__main__":
	main()