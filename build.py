import json
import os
import shutil
import mistune
from distutils.dir_util import copy_tree
from os.path import relpath

config = json.loads(str(open("config.json").read()))

mddir = config["mddir"]
outdir = config["outdir"]
assetdir = config["assetdir"]
defaultimg = config["defaultimg"]
homepagebase = open(config["homebasehtml"]).read()
mdhtmlbase = open(config["mdbasehtml"]).read()
cardbase = open(config["cardbasehtml"]).read()

markdown = mistune.Markdown()
def markup(md):
  return markdown(md)

def getDirContents(dir, filefilter):
  root, dirs, files = next(os.walk(dir))
  files = [file for file in files if file.endswith(filefilter)]
  return [files, dirs]

def getCardImg(name, dir):
  return name + ".png" if os.path.isfile(dir + name + ".png") else relpath(defaultimg, dir)

def buildPage(base, file, dir):
  return base.format(title = os.path.basename(file).replace(".html", ""), link = file, homelink = relpath(outdir, dir), content = markup(open(file).read()), assetdir = relpath(assetdir, dir))

def buildHomePage(filelist, dir):
  cardshtml = ""
  filelist[0].remove("index.html")
  for file in filelist[0]:
    cardshtml += cardbase.format(link = file, title = file.replace(".html", ""), image = getCardImg(file.replace(".html", ""), dir))
  for folder in filelist[1]:
    cardshtml += cardbase.format(link = folder, title = folder, image = getCardImg(folder.replace(".html", ""), dir))
  return homepagebase.format(cards = cardshtml, assetdir = relpath(assetdir, dir), homelink = relpath(outdir, dir))

def translateDir(dir):
  filelist = getDirContents(dir, ".md")
  for file in filelist[0]:
    if file.endswith(".md"):
      filename = file.replace(".md", ".html")
      os.rename(dir + file, dir + filename)
      page = buildPage(mdhtmlbase, dir + filename, dir)
      open(dir + filename, "w").write(page)
  open(dir + "/index.html", "w").write(buildHomePage(getDirContents(dir, ".html"), dir))

  for folder in filelist[1]:
    translateDir(dir + folder + "/")

def build():
  if os.path.exists(outdir):
    shutil.rmtree(outdir)
  os.makedirs(outdir)

  copy_tree(mddir, outdir)
  translateDir(outdir)

build()