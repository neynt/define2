#!/usr/bin/python
import sys
import os
import sqlite3
import re
import textwrap

GREY = '\033[1;30m'
LIGHT_GREY = '\033[37m'
RED = '\033[1;31m'
PURPLE = '\033[1;35m'
BLUE = '\033[1;34m'
YELLOW = '\033[33m'
GREEN = '\033[1;32m'
NO_COLOR = '\033[0m'

# Languages, in the order that they will be printed.
permitted_langs = [
    'French',
    'Lojban',
    'Translingual',
    'Mandarin',
    'Japanese',
    'English',
]
# With an empty permitted_langs, it prints all the languages found in alphabetical order.
#permitted_langs = []

wrapper = textwrap.TextWrapper(width=80, subsequent_indent=' ')

def chop(m):
    """Turns {{a|b|c}} into (a: b: c)""" 
    args = m.group(0).split('|')
    # Get rid of {{ }}
    args[0] = args[0][2:]
    args[-1] = args[-1][:-2]
    words = ': '.join(a for a in args if a)
    return YELLOW + '(' + words + ')' + NO_COLOR

def de_wikify(defn):
    """Turns Wiki markup into terminal-readable stuff."""
    # Gets rid of the '#' at the beginning
    defn = defn[1:]
    defn = defn.strip()

    # Regex component that matches a word.
    WORD = r'[^\[\]]+'

    # Get rid of comments
    #defn = re.sub(r'<!--(.*?)-->', '', defn)

    # Make comments grey
    defn = re.sub(r'<!--(.*?)-->', GREY + r' (\1)' + NO_COLOR, defn)

    # Get rid of <ref>, <sub>
    defn = re.sub(r'<ref>(.*?)</ref>', '', defn)

    # Remove <sub> tags (but keep contents)
    defn = re.sub(r'<sub>(.*?)</sub>', r'\1', defn)

    # Turn [[x|words]] into words
    defn = re.sub(r'\[\[(' + WORD + '?)\|(' + WORD + '?)\]\]', r'\2', defn)

    # Turn [[words]] into words
    defn = re.sub(r'\[\[(' + WORD + '?)\]\]', r'\1', defn)

    # Turn {{a|b|c}} into (a: b: c)
    defn = re.sub(r'\{\{(.+?)\}\}', chop, defn)

    # Make '''''word''''' purple, '''word''' red, and ''word'' blue.
    defn = re.sub(r"'''''(.+?)'''''", PURPLE + r'\1' + NO_COLOR, defn)
    defn = re.sub(r"'''(.+?)'''", RED + r'\1' + NO_COLOR, defn)
    defn = re.sub(r"''(.+?)''", BLUE + r'\1' + NO_COLOR, defn)

    # Fabulous word wrapping
    #defn = wrapper.fill(defn)

    return defn

if __name__ == '__main__':
    word_parts = []
    # Handle command line args
    for arg in sys.argv[1:]:
        if arg == '--html':
            GREY = '<span color="#888">'
            RED = '<span color="#f00">'
            PURPLE = '<span color="#f0f">'
            BLUE = '<span color="#00f">'
            YELLOW = '<span color="#ff0">'
            GREEN = '<span color="#0f0">'
            NO_COLOR = '</span>'
        elif arg == '--all':
            permitted_langs = []
        else:
            word_parts.append(arg)

    word = ' '.join(word_parts)

    # Query for words
    conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '/words.db')
    c = conn.cursor()
    results = {}

    for i, lang, role, defn in c.execute('''SELECT id, lang, role, defn FROM words WHERE word=?''', [word]):
        #print((i, lang, role, defn))
        if lang not in results:
            results[lang] = []
        results[lang].append((role, defn.strip()))
    
    if not permitted_langs:
        permitted_langs = sorted(results.keys())

    # Surround text with pretty newline characters
    print()
    if results:
        langs = [i for i in permitted_langs if i in results]
        other_langs = sorted([i for i in results if i not in langs])
        if langs:
            # Found words in permitted_langs, so print them all in order
            for lang in langs:
                print(GREEN + '' + lang + NO_COLOR)
                for role, defn in results[lang]:
                    print(GREY + '' + role + ": " + NO_COLOR + de_wikify(defn))
                print()
            if other_langs:
                print('"%s" is also in: %s' % (word, ', '.join(other_langs)))
                print()
        else:
            # If we found words but they're not in our permitted_langs,
            # print them anyways.
            print("'%s' was not found in: %s" % (word, ', '.join(permitted_langs)))
            print("But we did find this:")
            print()
            for lang in other_langs:
                print(GREEN + '### ' + lang + ' ###' + NO_COLOR)
                for role, defn in results[lang]:
                    print(GREY + role)
                    print('  ' + NO_COLOR + de_wikify(defn))
                print()
    else:
        print("'%s' was not found in any dictionary." % word) 
        print()
