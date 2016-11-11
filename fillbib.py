
'''
Query the ADS and INSPIRE databases to collect the citations used in a LaTeX file into a BibTeX file

Idea and main implementation is taken by Michele Vallisneri, see http://www.vallis.org/salon/summary-2.html
I changed the script to avoid the requests module, and added the INSPIRE database part.

Usage:
python fillbib.py <tex_file> <bib_file>. If <bib_file> is absent, it will try to guess it from the aux file"

'''
import sys, os, re, commands

if len(sys.argv)==2:     # Get the name of the bibfile from the aux file
    basename = sys.argv[1].split('.tex')[0]
    auxfile = basename + '.aux'
    for line in open(auxfile,'r'):
        m = re.search(r'\\bibdata\{(.*)\}',line)   # match \citation{...}, collect the ... note that we escape \, {, and }
        if m:
            bibfile = filter(lambda x:x!=basename+'Notes', m.group(1).split(','))[0]  # Remove that annyoing feature of revtex which creates a *Notes.bib bibfile. Note this is not solid if you want to handle multiple bib files.
    bibfile = bibfile + '.bib'

elif len(sys.argv)==3:    # Bibfile specified from argv
    basename = sys.argv[1].split('.tex')[0]
    auxfile = basename + '.aux'
    bibfile = sys.argv[2].split('.bib')[0] + '.bib'
else:
    print "Usage: python fillbib.py <tex_file> <bib_file>. If <bib_file> is absent, assume the two are the same."
    sys.exit()


# Get all citations from aux file. Citations will look like \citation{2004PhRvD..69j4017P,2004PhRvD..69j4017P}
cites = set() # use a set (no repetitions)
for line in open(auxfile,'r'):
    m = re.search(r'\\citation\{(.*)\}',line)   # find \citation{...}
    if m:
        cites.update(m.group(1).split(','))     # split by commas

cites= cites.difference(['REVTEX41Control','apsrev41Control']) # Remove annoying entries of revtex

print "Seek:", cites

# Check what you already have in the bib file
haves = []
if os.path.isfile(bibfile):
    for line in open(bibfile,'r'):
        m = re.search(r'@.*?\{(.*),',line)  # .*\{ means "any # of any char followed by {"; .*?\{ means "the shortest string matching any # of any char followed by {"
        if m:
            haves.append(m.group(1))
print "Have:", haves


# Query ADS and INSPIRE
bibtex = open(bibfile,'a')      # open for appending

for c in cites:
    if c not in haves:

        if not c[0].isalpha(): # The first charachet is a number: could be on ADS

            try:
                bib = "@"+commands.getstatusoutput('curl "http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode='+c+'&data_type=BIBTEX&db_key=AST&nocookieset=1"')[1].split("@")[1]
                bibtex.write(bib)
                print "ADS Found:", c
            except:
                print "ADS Not found:", c

        else: # The first charachet is not a number: could be on INSPIRE

            try:
                bib = "@"+commands.getstatusoutput('curl "https://inspirehep.net/search?p='+c+'&of=hx&em=B&sf=year&so=d&rg=1"')[1].split("@")[1].split('</pre>')[-2]
                bibtex.write(bib)
                print "INSPIRE Found:", c
            except:
                print "INSPIRE Not found:", c

bibtex.close()
