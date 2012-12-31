#!/usr/bin/python
import sqlite3
from urllib.request import urlopen
import gzip
import os

DEF_FILE = ''

# Prompt user for dictionary choice.
print("You are about to create a dictionary database.")
print("Which definition dump do you want to use?")
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
conn = sqlite3.connect('words.db')
c = conn.cursor()
c.execute("""DROP TABLE IF EXISTS words""")
c.execute("""CREATE TABLE words (id int, lang text, word text, role text, defn text)""")

with gzip.open(DEF_FILE) as f:
    # Populate the table with entries.
    print("Inserting definitions into database.")
    for i,l in enumerate(f):
        if i != 0 and i%100000 == 0:
            print("%.1f million definitions inserted." % (i/1000000))
        s = str(l, encoding='utf-8')
        c.execute('INSERT INTO words VALUES (?,?,?,?,?)', [i]+s.split('\t'))
    f.close()

# Create index for blazing fast access.
print("Creating database index.")
c.execute("""CREATE INDEX word_index ON words (word)""")
conn.commit()

print("We're all done! Try\n./define2.py myrrh")
