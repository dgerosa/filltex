#!/usr/bin/env python

'''
Query the ADS and INSPIRE databases to collect the citations used in a LaTeX file into a BibTeX file

Idea and main implementation is taken by Michele Vallisneri, see http://www.vallis.org/salon/summary-2.html
I changed the script to avoid the requests module, and added the INSPIRE database part.

Usage:
python fillbib.py <tex_file> <bib_file>. If <bib_file> is absent, it will try to guess it from the aux file"

'''
from __future__ import absolute_import, print_function
import argparse
import sys, os, re, html
import json

if sys.version_info.major>=3:
    import urllib.request as urllib
else:
    import urllib


def ads_citation(c): # download single ADS citation
    #f= urllib.urlopen("http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode="+c+"&data_type=BIBTEX&db_key=AST&nocookieset=1")
    #print("http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode="+c+"&data_type=BIBTEX&db_key=AST&nocookieset=1")
    f= urllib.urlopen("https://ui.adsabs.harvard.edu/abs/"+c+"/exportcitation")

    bib = f.read()
    f.close()
    if sys.version_info.major>=3:
        bib=bib.decode()
    bib = "@"+list(filter(lambda x:'adsnote' in x, bib.split("@")))[0].split("</textarea>")[0]
    bib=html.unescape(bib)

    if 'arXiv' in c: # Take care of preprint on ADS
        bib = bib.split("{")[0]+"{"+c+","+",".join(bib.split(",")[1:])
        return bib

    elif bib.split("{")[1].split(',')[0] == c: # Check you got what you where looking for
        return bib
    else:
        return None

def inspire_citation(key,
        generate=False,
        max_num_authors=None,
        num_authors_short=None,
        journal_arXiv_fallback=False):
    """
    Generate a custom BiBTeX entry

    * generate
        if True we generate the BibTeX rather than using the default from iNSPIRE
    * max_num_authors
        maximum number of authors to include (all of them if None)
    * num_authors_short
        number of authors to include if the number of authors is longer than max_num_authors
        if not specified, this defaults to max_num_authors
    * journal_arXiv_fallback
        use arXiv:eprint as the journal field if no journal is found
    """
    request = 'https://inspirehep.net/api/literature?q=' + key
    data = json.loads(urllib.urlopen(request).read())
    if data['hits']['total'] != 1:
        return None
    if not generate:
        bib = urllib.urlopen(data['hits']['hits'][0]['links']['bibtex']).read()
        inspire_key = data['hits']['hits'][0]['metadata']['texkeys'][0]
        if sys.version_info.major >= 3:
            return bib.decode().replace(inspire_key, key)
        else:
            return bib.replace(inspire_key, key)
    metadata = data['hits']['hits'][0]['metadata']

    doctype = metadata["document_type"][0]

    # BibTeX entry as a dictionary
    bibtex = {}

    # Find all authors
    if "authors" in metadata:
        num_authors = len(metadata["authors"])
        if max_num_authors is not None and num_authors > max_num_authors:
            short_author_list = True
            if num_authors_short is None:
                num_authors_short = max_num_authors
        else:
            short_author_list = False
        author_list = []
        for idx, author in enumerate(metadata['authors']):
            if short_author_list and idx >= num_authors_short:
                author_list.append("others")
                break
            author_list.append(author['full_name'])
        bibtex['author'] = " and ".join(author_list)

    # Find all collaborations
    if "collaborations" in metadata:
        collab_list = []
        for collab in metadata["collaborations"]:
            collab_list.append(collab["value"])
        bibtex["collaboration"] = ", ".join(collab_list)

    try:
        bibtex["title"] = "{" + metadata["titles"][0]["title"] + "}"
    except KeyError:
        pass

    try:
        bibtex["eprint"] = metadata["arxiv_eprints"][0]["value"]
        bibtex["archivePrefix"] = "arXiv"
        bibtex["primaryClass"] = metadata["arxiv_eprints"][0]["categories"][0]
    except KeyError:
        pass

    try:
        bibtex["doi"] = metadata["dois"][0]["value"]
    except KeyError:
        pass

    try:
        bibtex["journal"] = metadata["publication_info"][0]["journal_title"]
    except KeyError:
        if journal_arXiv_fallback:
            bibtex["journal"] = "arXiv:" + bibtex["eprint"]
        pass

    try:
        bibtex["volume"] = metadata["publication_info"][0]["journal_volume"]
    except KeyError:
        pass

    try:
        bibtex["number"] = metadata["publication_info"][0]["journal_issue"]
    except KeyError:
        pass

    try:
        bibtex["pages"] = metadata["publication_info"][0]["page_start"]
    except KeyError:
        pass

    try:
        bibtex["year"] = metadata["publication_info"][0]["year"]
    except KeyError:
        try:
            bibtex["year"] = metadata["preprint_date"][0:4]
            bibtex["month"] = str(int(metadata["preprint_date"][5:7]))
        except KeyError:
            pass

    # Format BibTeX entry
    s = "@{}{{{}".format(doctype, key)
    for field, value in bibtex.items():
        s += ",\n    {} = \"{}\"".format(field, value)
    s += "\n}"

    return s

def test_ads(): # test single ADS web scraping (both published articles and preprints)
    test_key = ["2016PhRvL.116f1102A","2016arXiv160203837T"]
    known_output= '@ARTICLE{2016PhRvL.116f1102A,\n   author = {{Abbott}, B.~P. and {Abbott}, R. and {Abbott}, T.~D. and {Abernathy}, M.~R. and \n\t{Acernese}, F. and {Ackley}, K. and {Adams}, C. and {Adams}, T. and \n\t{Addesso}, P. and {Adhikari}, R.~X. and et al.},\n    title = "{Observation of Gravitational Waves from a Binary Black Hole Merger}",\n  journal = {Physical Review Letters},\narchivePrefix = "arXiv",\n   eprint = {1602.03837},\n primaryClass = "gr-qc",\n     year = 2016,\n    month = feb,\n   volume = 116,\n   number = 6,\n      eid = {061102},\n    pages = {061102},\n      doi = {10.1103/PhysRevLett.116.061102},\n   adsurl = {http://adsabs.harvard.edu/abs/2016PhRvL.116f1102A},\n  adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n}\n\n'
    assert [ads_citation(tk) == known_output for tk in test_key]

def test_inspire(): # test single INSPIRE web scraping
    test_key = "Abbott:2016blz"
    known_output = '@article{Abbott:2016blz,\n    author = "Abbott, B.P. and Abbott, R. and Abbott, T.D. and Abernathy, M.R. and Acernese, F. and others",\n    collaboration = "LIGO Scientific, Virgo",\n    title = "{Observation of Gravitational Waves from a Binary Black Hole Merger}",\n    eprint = "1602.03837",\n    archivePrefix = "arXiv",\n    primaryClass = "gr-qc",\n    doi = "10.1103/PhysRevLett.116.061102",\n    journal = "Phys.Rev.Lett.",\n    volume = "116",\n    number = "6",\n    year = "2016"\n}'
    assert inspire_citation(test_key, generate=True, max_num_authors=5) == known_output


def fillbib_tex(args):
    if args.bibtex is None:     # Get the name of the bibfile from the aux file
        basename = args.texfile[0].split('.tex')[0]
        auxfile = basename + '.aux'
        for line in open(auxfile,'r'):
            m = re.search(r'\\bibdata\{(.*)\}',line)   # match \citation{...}, collect the ... note that we escape \, {, and }
            if m:
                bibfile = list(filter(lambda x:x!=basename+'Notes', m.group(1).split(',')))[0]  # Remove that annyoing feature of revtex which creates a *Notes.bib bibfile. Note this is not solid if you want to handle multiple bib files.
        bibfile = bibfile + '.bib'

    else:    # Bibfile specified from argv
        basename = args.texfile[0].split('.tex')[0]
        auxfile = basename + '.aux'
        bibfile = args.bibtex.split('.bib')[0] + '.bib'


    # Get all citations from aux file. Citations will look like \citation{2004PhRvD..69j4017P,2004PhRvD..69j4017P}
    cites = set() # use a set (no repetitions)
    for line in open(auxfile,'r'):
        m = re.search(r'\\citation\{(.*)\}',line)   # find \citation{...}
        if m:
            cites.update(m.group(1).split(','))     # split by commas

    cites= cites.difference([
        'REVTEX41Control','apsrev41Control',
        'REVTEX42Control','apsrev42Control']) # Remove annoying entries of revtex

    print("Seek:", cites)

    # Check what you already have in the bib file
    haves = []
    if os.path.isfile(bibfile):
        for line in open(bibfile,'r'):
            m = re.search(r'@.*?\{(.*),',line)  # .*\{ means "any # of any char followed by {"; .*?\{ means "the shortest string matching any # of any char followed by {"
            if m:
                haves.append(m.group(1))
    print("Have:", haves)


    # Query ADS and INSPIRE
    bibtex = open(bibfile,'a')      # open for appending

    for c in cites:
        if c and c not in haves: # c is something and you don't have it already

            if not c[0].isalpha(): # The first charachter is a number: could be on ADS

                try:
                    bib = ads_citation(c)
                    bibtex.write(bib)
                    print("ADS Found:", c)
                except:
                    print("ADS Not found:", c)

            else: # The first charachter is not a number: could be on INSPIRE

                try:
                    bib = inspire_citation(c,
                        generate=args.generate,
                        max_num_authors=args.max_num_authors,
                        num_authors_short=args.num_authors_short,
                        journal_arXiv_fallback=args.journal_arXiv_fallback)
                    bibtex.write(bib)
                    print("INSPIRE Found:", c)
                except:
                    print("INSPIRE Not found:", c)

    bibtex.close()

def fillbib_list(args):
    for c in args.keys:
        if not c[0].isalpha():
            bib = ads_citation(c)
            if bib is None:
                sys.stderr.write("ADS Not Found: {}\n".format(c))
            else:
                print(bib)
        else:
            bib = inspire_citation(c,
                    generate=args.generate,
                    max_num_authors=args.max_num_authors,
                    num_authors_short=args.num_authors_short,
                    journal_arXiv_fallback=args.journal_arXiv_fallback)
            if bib is None:
                sys.stderr.write("INSPIRE Not Found: {}\n".format(c))
            else:
                print(bib)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true",
            help="Generate the BibTeX entries from the metadata "
                "(this is useful to customize the generated BiBTeX file)")
    parser.add_argument("--journal_arXiv_fallback", dest="journal_arXiv_fallback", action="store_true",
            help="Set the journal entry to be arXiv for unpublished preprints "
                "(iNSPIRE entries only, requres --generate)")
    parser.add_argument("--max-num-authors", dest="max_num_authors", type=int,
            help="Include at most this many authors for each bibtex entry"
                "(iNSPIRE entries only, requres --generate)")
    parser.add_argument("--num-authors-short", type=int,
            help="Number of authors to list if the number of authors is larger than max_num_authors"
                "(iNSPIRE entries only, defaults to max-num-authors, requres --generate)")
    subparsers = parser.add_subparsers(help="Subcommands")

    parser_tex = subparsers.add_parser("tex", help="Create a bibliography for a tex document")
    parser_tex.add_argument("--bibtex", help="The BiBTeX file to use (if not specified we try to find out)")
    parser_tex.add_argument("texfile", nargs=1, help="The (La)TeX file to process")
    parser_tex.set_defaults(func=fillbib_tex)

    parser_list = subparsers.add_parser("list", help="Create a bibliography given a list of ADS/iNSPIRE keys")
    parser_list.add_argument("keys", nargs="+", help="ADS/iNSPIRE keys to fetch")
    parser_list.set_defaults(func=fillbib_list)

    args = parser.parse_args()
    try:
        args.func(args)
    except:
        parser.print_usage()
