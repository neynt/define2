#!/usr/bin/python
import sqlite3
from urllib.request import urlopen
import gzip
import sys

DEF_FILE = ''
DB_FILE = 'words.db'

# Prompt user for dictionary choice.
print("You are about to create a dictionary database.")
print("Which definition dump do you want to download?")
print(" [1] Just English words (~15MB download, ~100MB installed)")
print(" [2] ALL the languages! (~50MB download, ~550MB installed)")
print(" [3] Use existing file")
print("> ", end='')
choice = input()
if choice.startswith('1'):
    DEF_FILE = 'enwikt-defs-latest-en.tsv.gz'
    print("Just English it is.")
    dl = True
elif choice.startswith('2'):
    DEF_FILE = 'enwikt-defs-latest-all.tsv.gz'
    print("Okay, I'll get every single language.")
    dl = True
else:
    print("File name > ", end='')
    DEF_FILE = input()
    dl = False

if dl:
    print("Downloading to %s." % DEF_FILE)
    dgz = urlopen('http://toolserver.org/~enwikt/definitions/%s' % DEF_FILE)
    with open(DEF_FILE, 'wb') as f:
        f.write(dgz.read())
        f.close()

print("Creating database.")
# Truncate current database
open(DB_FILE, 'w').close()
# Create new database
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("""DROP TABLE IF EXISTS words""")
c.execute("""CREATE TABLE words (id int, lang text, word text, role text, defn text)""")

# Populate the table with entries.
with gzip.open(DEF_FILE) as f:
    print("Inserting definitions into database.")
    for i,l in enumerate(f):
        if i == 100000:
            print("%.1f million definitions inserted." % (i/1000000), end='')
            sys.stdout.flush()
        elif i != 0 and i%100000 == 0:
            print("\r%.1f million definitions inserted." % (i/1000000), end='')
            sys.stdout.flush()
        s = str(l, encoding='utf-8')
        c.execute('INSERT INTO words VALUES (?,?,?,?,?)', [i]+s.split('\t'))
    f.close()

# Create index for blazing fast access.
print("Creating database index.")
c.execute("""CREATE INDEX word_index ON words (word)""")
conn.commit()

print("We're all done! Try\n./define2.py myrrh")
