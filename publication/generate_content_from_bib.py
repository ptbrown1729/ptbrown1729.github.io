"""
Given a bibtex file, generate toml configuration files

Here is the idea: when you want to add a new publication, add it to the file "pubs.bib". Then run this file to
automatically generate a folder containing an "index.md" and "cite.bib" file.

todo: latex is not correctly rendered in the author's names, and have problems with non ascii characters in the abstracts
"""
import bibtexparser
import os
import datetime

# todo: make this more robust to entries not being present
def write_config_file(bibtex_entry, fname):

  authors = bibtex_entry['author'].split(" and ")
  title = bibtex_entry['title'].replace("{", "").replace("}", "") # todo: remove braces {} and etc

  doi = bibtex_entry['doi']
  try:
    journal = bibtex_entry['journal']
  except KeyError:
    journal = None

  try:
    volume = int(bibtex_entry['volume'])
  except KeyError:
    volume = None

  try:
    number = int(bibtex_entry['number'])
  except KeyError:
    number = None

  year = int(bibtex_entry['year'])
  month = datetime.datetime.strptime(bibtex_entry['month'], "%b").month
  day = 1

  try:
    url_preprint = entry['eprint']
  except KeyError:
    url_preprint = ""

  md_file = "---\ntitle: \"%s\"\nauthors:\n" % title
  for a in authors:
    md_file += "- %s\n" % a

  md_file += "date: \"%04d-%02d-%02dT00:00:00Z\"\n" % (year, month, day)
  md_file += "doi: \"%s\"\n" % doi
  md_file += "\n# Schedule page publish date (NOT publication's date).\n" \
             "publishDate: \"2017-01-01T00:00:00Z\"\n"
  md_file += "\n# Publication type.\n" \
             "# Legend: 0 = Uncategorized; 1 = Conference paper; 2 = Journal article;\n" \
             "# 3 = Preprint / Working Paper; 4 = Report; 5 = Book; 6 = Book section;\n" \
             "# 7 = Thesis; 8 = Patent\n" \
             "publication_types: [\"2\"]\n"

  if not journal is None and not volume is None and not number is None:
    md_file += "\n# Publication name and optional abbreviated publication name.\n" \
               "publication: \"*%s*, <b>%d</b> %d (%04d)\"\n" \
               "publication_short: \"\"\n" % (journal, volume, number, year)
  else:
    md_file += "\n# Publication name and optional abbreviated publication name.\n" \
               "publication: \"\"\n" \
               "publication_short: \"\"\n"

  md_file += "\nabstract: \"%s\"\n" % bibtex_entry['abstract']

  md_file += "\n# Summary. An optional shortened abstract.\n" \
             "summary:\n"

  md_file += "\ntags:\n- Source Themes\nfeatured: false\n"

  md_file += "\n# links:\n" \
             "# - name: \"\"\n" \
             "#   url: \"\"\n" \
             "url_preprint: '%s'\n" \
             "url_pdf: ''\n" \
             "url_code: \'\'\n" \
             "url_dataset: \'\'\n" \
             "url_poster: \'\'\n" \
             "url_project: \'\'\n" \
             "url_slides: \'\'\n" \
             "url_source: \'\'\n" \
             "url_video: \'\'\n" % url_preprint

  md_file += "\n# Featured image\n" \
             "# To use, add an image named `featured.jpg/png` to your page's folder.\n" \
             "image:\n" \
             "  caption: \'Image credit: [**Unsplash**](https://unsplash.com/photos/jdD8gXaTZsc)\'\n" \
             "  focal_point: \"\"\n" \
             "  preview_only: false\n"

  md_file += "\n# Associated Projects (optional).\n" \
             "#   Associate this publication with one or more of your projects.\n" \
             "#   Simply enter your project's folder or file name without extension.\n" \
             "#   E.g. `internal-project` references `content/project/internal-project/index.md`.\n" \
             "#   Otherwise, set `projects: []`.\n" \
             "projects: []\n"
  md_file += "---"

  with open(fname, "w") as f:
    f.write(md_file)

  return md_file

if __name__ == "__main__":
  bibtex_fname = "pubs.bib"
  citation_fname = "cite.bib"
  md_fname = "index.md"

  file_dir = os.path.dirname(__file__)
  bibtex_fpath = os.path.join(file_dir, bibtex_fname)

  with open(bibtex_fpath, "rb") as f:
    bib_data = bibtexparser.load(f)

  for entry in bib_data.entries:
    ename = entry['title'].replace(" ", "_").replace("-", "_").lower()
    chars = "\\`*{}[]()>#+.!$"
    for c in chars:
      ename = ename.replace(c, "")
    ename = ename.encode("ascii", "ignore").decode("ascii")

    # create directory
    dir_path = os.path.join(file_dir, ename)
    if not os.path.exists(dir_path):
      os.mkdir(dir_path)
    else:
      print("%s already exists. Not overwriting." % dir_path)
      continue

    # write citation file
    # create bibtex database with one entry
    db = bibtexparser.bibdatabase.BibDatabase()

    # todo: had trouble with writing non-ascii characters. so removing them for the moment, but would love
    # to solve this
    entry['abstract'] = entry['abstract'].encode("ascii", "ignore").decode("ascii")
    db.entries = [entry]

    # todo: how to handle utf-8 or unicode strings that break this?
    writer = bibtexparser.bwriter.BibTexWriter()
    with open(os.path.join(dir_path, citation_fname), "w") as f:
      f.write(writer.write(db))

    # write toml file
    fpath_md = os.path.join(dir_path, md_fname)
    write_config_file(entry, fpath_md)

