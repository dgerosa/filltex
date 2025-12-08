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

import token
import urllib.request
import requests

# def ads_citation(c): # download single ADS citation
#     #f= urllib.urlopen("http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode="+c+"&data_type=BIBTEX&db_key=AST&nocookieset=1")
#     #print("http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode="+c+"&data_type=BIBTEX&db_key=AST&nocookieset=1")
#     f= urllib.urlopen("https://ui.adsabs.harvard.edu/abs/"+c+"/exportcitation")

#     bib = f.read()
#     f.close()
#     if sys.version_info.major>=3:
#         bib=bib.decode()
#     bib = "@"+list(filter(lambda x:'adsnote' in x, bib.split("@")))[0].split("</textarea>")[0]
#     bib=html.unescape(bib)

#     return bib


def ads_citation(c): 
    """
    Download a single ADS citation. Uses ADS_TOKEN if available; otherwise falls back to UI scrape.

    Parameters:
        c (str): ADS bibcode

    Returns:
        str: BibTeX citation
    """
    token = os.environ.get('ADS_TOKEN')
    if token:
        # Use ADS API with token

        results = requests.get(f"https://api.adsabs.harvard.edu/v1/export/bibtex/{c}", headers={'Authorization': 'Bearer ' + token})
        bib = results.text

    else:
        print('No ADS_TOKEN found in environment; falling back to UI scrape.', file=sys.stderr)
        # Fall back to UI scrape
        url = f"https://ui.adsabs.harvard.edu/abs/{c}/exportcitation"
        with urllib.request.urlopen(url) as f:
            bib = f.read().decode()
            # Extract the BibTeX entry
            bib = "@"+list(filter(lambda x:'adsnote' in x, bib.split("@")))[0].split("</textarea>")[0]
            bib = html.unescape(bib)

    return bib

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
    data = json.loads(urllib.request.urlopen(request).read())
    if data['hits']['total'] != 1:
        return None
    if not generate:
        bib = urllib.request.urlopen(data['hits']['hits'][0]['links']['bibtex']).read()
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

    if args.updatepublished:
        with open(basename+".tex", 'r') as texfile:
            texdata = texfile.read()

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

                    cfound = bib.split("{")[1].split(',')[0]
                    
                    if  cfound == c: # Check you got what you where looking for
                        pass
                    elif 'arXiv' in c: # Take care of preprint on ADS

                        if args.updatepublished and '.tmp.' not in cfound:
                            print("ADS replace", c, "-->", cfound)
                            # This substitute the new ID into the tex file. Use at your own risk. The .tmp. condition fixes those stupid MNRAS temp entries.
                            texdata = texdata.replace(c, cfound)

                        else: 
                            # This subsitute the arxiv id back in to the bib file
                            bib = bib.split("{")[0]+"{"+c+","+",".join(bib.split(",")[1:])

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

    if args.updatepublished:
        with open(basename+".tex", 'w') as texfile:
            texfile.write(texdata)

    # Clean up journal names
    if args.journals:
        journals(bibfile)

    
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


def curly(x):
   '''Just a curly bracket sandwich.'''
   return "{"+x+"}"

def journals(bibfile):
    '''
    Clean up the names of some journals using their ISO4 standards.
    Journal abbreviations are taken from https://images.webofknowledge.com/images/help/WOS/A_abrvjt.html
    If your favourite journal is missing, please add it and send a pull request. Thanks!
    '''

    # The format is: [ADS name, INSPIRE name, ISO4 abbreviation]
    journals = [
            ####
            # These are the journals from the ADS macros: https://ui.adsabs.harvard.edu/help/actions/journal-macros
            # I could not find them all on INSPIRE, some are missing.
            ####
            ['\\aj', 'Astron. J.', 'Astron. J.'],
            ['\\actaa', 'Acta Astron.', 'Acta Astronom.'],
            ['\\araa', 'Ann. Rev. Astron. Astrophys.', 'Annu. Rev. Astron. Astrophys.'],
            ['\\apj', 'Astrophys. J.', 'Astrophys. J.'],
            ['\\apjl', 'Astrophys. J. Lett.', 'Astrophys. J. Lett.'],
            ['\\apjs', 'Astrophys. J. Suppl.', 'Astrophys. J. Supp. S.'],
            ['\\ao', 'Appl. Opt.', 'Appl. Optics'],
            ['\\apss', 'Astrophys. Space Sci.', 'Astrophys. Space Sci.'],
            ['\\aap', 'Astron. Astrophys.', 'Astron. Astrophys.'],
            ['\\aapr', 'Astron. Astrophys. Rev.', 'Astron. Astrophys. Rev.'],
            ['\\aaps', 'Astron. Astrophys. Suppl. Ser.', 'Astron. Astrophys. Sup.'],
            ['\\azh', '', 'Astron. Zh.'], #Not sure. Various names on inspire
            ['\\baas', 'Bull. Am. Astron. Soc.', 'Bull. Am. Astron. Soc.'],
            ['\\bac', 'Bull. Astron. Inst. Czech.', 'B. Astron. I. Czech.'],
            ['\\caa', 'Chin. Astron. Astrophys.', 'Chinese Astron. Astr.'],
            ['\\cjaa', 'Chin. J. Astron. Astrophys.', 'Chinese J. Astron. Ast.'],
            ['\\icarus', 'Icarus', 'Icarus'],
            ['\\jcap', 'JCAP', 'J. Cosmology Astropart. Phys.'],
            ['\\jrasc', 'J. Roy. Astron. Soc. Canada', 'J. Roy Astron. Soc. Can.'],
            ['\\memras', 'Mem. Roy. Astron. Soc.', 'Mem. R. Astron. Soc.'],
            ['\\mnras', 'Mon. Not. Roy. Astron. Soc.', 'Mon. Not. R. Astron. Soc.'],
            ['\\na', 'New Astron.', 'New Astron.'],
            ['\\nar', 'New Astron. Rev.', 'New Astron. Rev.'],
            ['\\pra', 'Phys. Rev. A', 'Phys. Rev. A'],
            ['\\prb', 'Phys. Rev. B', 'Phys. Rev. B'],
            ['\\prc', 'Phys. Rev. C', 'Phys. Rev. C'],
            ['\\prd', 'Phys. Rev. D', 'Phys. Rev. D'],
            ['\\pre', 'Phys. Rev. E', 'Phys. Rev. E'],
            ['\\prl', 'Phys. Rev. Lett.', 'Phys. Rev. Lett.'],
            ['\\pasa', 'Publ. Astron. Soc. Austral.', 'Publ. Astron. Soc. Aust.'],
            ['\\pasp', 'Publ. Astron. Soc. Pac.', 'Publ. Astron. Soc. Pac.'],
            ['\\pasj', 'Publ. Astron. Soc. Jap.', 'Publ. Astron. Soc. Jpn.'],
            ['\\rmxaa', 'Rev. Mex. Astron. Astrofis.', 'Rev. Mex. Astron. Astr.'],
            ['\\qjras', 'Q. J. Roy. Astron. Soc.', 'Q. J. Roy. Astron. Soc.'],
            ['\\skytel', 'Sky Telesc.', 'Sky Telescope'],
            ['\\solphys', 'Solar Phys.', 'Sol. Phys.'],
            ['\\sovast', 'Sov. Astron.', 'Sov. Astron.'],
            ['\\ssr', 'Space Sci. Rev.', 'Space Sci. Rev.'],
            ['\\zap', 'Z. Astrophys.', 'Z. Astrophys.'],
            ['\\nat', 'Nature', 'Nature'],
            ['\\iaucirc', 'IAU Circ.', 'IAU Circ.'],
            ['\\aplett', 'Astrophys. Lett.', 'Astrophys. Lett.'],
            ['\\apspr', '', 'Astrophys.~Space~Phys.~Res.'], #Could not find it on INSPIRE
            ['\\bain', 'Bull. Astron. Inst. Netherlands', 'B. Astron. I. Neth.'],
            ['\\fcp', 'Fund. Cosmic Phys.', 'Fund. Cosmic Phys.'],
            ['\\gca', 'Geochim. Cosmochim. Acta', 'Geochim. Cosmochim. Ac.'],
            ['\\grl', 'Geophys. Res. Lett.', 'Geophys. Res. Lett.'],
            ['\\jcp', 'J. Chem. Phys.', 'J. Chem. Phys.'],
            ['\\jgr', 'J. Geophys. Res.', 'J. Geophys. Res.'],
            ['\\jqsrt', 'J. Quant. Spectrosc. Radiat. Trans.', 'J. Quant. Sprectrosc. Ra.'],
            ['\\memsai', 'Mem. Soc. Ast. It.', 'Mem. Soc. Astron. Ital.'],
            ['\\nphysa', 'Nucl. Phys. A', 'Nucl. Phys. A'],
            ['\\physrep', 'Phys. Rept.', 'Phys. Rep.'],
            ['\\physscr', 'Phys. Scripta', 'Phys. Scripta'],
            ['\\planss', 'Planet. Space Sci.', 'Planet. Space Sci.'],
            ['\\procspie', 'Proc. SPIE Int. Soc. Opt. Eng.', 'P. Soc. Photo.-Opt. Ins.'],
            ####
            # [Davide Gerosa] These are journals that I personally encountered. 
            # Will keep on adding to this list.
            ####
            ['Advances in Space Research','Adv. Space Res.','Adv. Space Res.'], #ISI list not correct
            ['American Institute of Physics Conference Series','AIP Conf. Proc.','AIP Conf. Proc.'],
            ['American Journal of Physics','Am. J. Phys.','Am. J. Phys.'],
            ['Annals of Data Science','Ann. Data Sci.','Ann. Data Sci.'],
            ['Astronomy and Computing','Astron. Comput.','Astron. Comput.'],
            ['Astroparticle Physics','Astropart. Phys.','Astropart. Phys.'],
            ['Astrophysics and Space Science Library','Astrophys. Space Sci. Libr.','Astrophys. Space Sc. L.'],
            ['Astrophysics and Space Science Library','Astrophys. Space Sci. Libr.','Astrophys. Space Sc. L.'],
            ['Bulletin of the American Astronomical Society','Bull. Am. Astron. Soc.','Bull. Am. Astron. Soc.'],
            ['Classical and Quantum Gravity','Class. Quant. Grav.','Class. Quantum Grav.'], #ISI list not correct
            ['Communications in Mathematical Physics', 'Commun. Math. Phys.', 'Commun. Math. Phys.'],
            ['European Physical Journal C', 'Eur. Phys. J. C', 'Eur. Phys. J. C'],
            ['Frontiers in Astronomy and Space Sciences','Front. Astron. Space Sci.','Front. Astron. Space Sci.'],
            ['General Relativity and Gravitation', 'Gen. Rel. Grav.', 'Gen. Relat. Gravit.'],
            ['International Journal of Modern Physics D', 'Int. J. Mod. Phys. D', 'Int. J. Mod. Phys. D'], 
            ['iScience', 'iScience', 'iScience'], 
            ['Journal of High Energy Physics','JHEP','J. High Energy Phys.'],
            ['Journal of Machine Learning Research','J. Machine Learning Res.','J. Mach. Learn. Res.'],
            ['Journal of Mathematical Analysis and Applications','J. Math. Anal. Appl.','J. Math. Anal. Appl'],
            ['Journal of Physics Conference Series','J. Phys. Conf. Ser.','J. Phys. Conf. Ser.'],
            ['Journal of Statistical Physics','J. Statist. Phys.','J. Stat. Phys.'],
            ['Journal of the Royal Statistical Society B','J. Roy. Statist. Soc. B','J. Roy. Statist. Soc. B'],
            ['Living Reviews in Relativity', 'Living Rev. Rel.', 'Living Rev. Relativ.'],
            ['Machine Learning: Science and Technology','Mach. Learn. Sci. Tech.','Mach. Learn. Sci. Tech.'], #ISI list not correct
            ['Machine Learning','Machine Learning','Mach. Learn.'],
            ['Nature Astronomy', 'Nature Astron.', 'Nat. Astron.'],
            ['Nature Methods', 'Nature Meth.', 'Nat. Methods'],
            ['Nature Reviews Physics','Nature Rev. Phys.','Nat. Rev. Phys.'],
            ['Physica A Statistical Mechanics and its Applications','Physica A','Physica A'],
            ['Physica D Nonlinear Phenomena', 'Physica D', 'Physica D'],
            ['Physical Review', 'Phys. Rev.', 'Phys. Rev.'],
            ['Physical Review Research', 'Phys. Rev. Res.', 'Phys. Rev. Res.'],
            ['Physical Review X', 'Phys. Rev. X', 'Phys. Rev. X'],
            ['Physics Letters A', 'Phys. Lett. A', 'Phys. Lett. A'],
            ['Proceedings of the Royal Society of London Series A', 'Proc. Roy. Soc. Lond. A', 'P. R. Soc. Lond. A'],
            ['Proceedings of the National Academy of Science', 'Proc. Nat. Acad. Sci.', 'Proc. Natl. Acad. Sci. USA'],
            ['Progress of Theoretical and Experimental Physics', 'PTEP', 'Prog. Theor. Exp. Phys.'],
            ['Rendiconti Lincei. Scienze Fisiche e Naturali', 'Rend. Lincei Sci. Fis. Nat.', 'Rend. Lincei-Sci. Fis.'],
            ['Reports on Progress in Physics', 'Rept. Prog. Phys.', 'Rep. Prog. Phys.'],
            ['Research Notes of the American Astronomical Society', 'Res. Notes AAS','Res. Notes AAS'],
            ['Reviews of Modern Physics', 'Rev. Mod. Phys.', 'Rev. Mod. Phys.'],
            ['Science Advances','Sci. Adv.','Sci. Adv.'],
            ['SIAM Journal on Scientific Computing','SIAM J. Sci. Comput.','SIAM J. Sci. Comput.'],
            ['The Journal of Open Source Software','J. Open Source Softw.','J. Open Source Softw.'],
            ]

    with open(bibfile, 'r') as bibtex :
        filedata = bibtex.read()

    for j in journals:
        print(j)
        if j[0]:
            filedata = filedata.replace(curly(j[0]), curly(j[2]))
        if j[1]:
            filedata = filedata.replace(curly(j[1]), curly(j[2]))
            filedata = filedata.replace('journal = "'+j[1], 'journal = "'+j[2])

    ### Clean up arxiv repeated information in ADS records:
    filedata = filedata.replace('arXiv e-prints', '{}')
    filedata = re.sub('pages = {arXiv:[0-9]+.[0-9]+},','',filedata)
    filedata = re.sub('Pages = {arXiv:[0-9]+.[0-9]+},','',filedata)
    filedata = re.sub('eid = {arXiv:[0-9]+.[0-9]+},','',filedata)
    filedata = re.sub('Eid = {arXiv:[0-9]+.[0-9]+},','',filedata)
    filedata = re.sub('doi = {[0-9]+.[0-9]+/arXiv.[0-9]+.[0-9]+},','',filedata)

    with open(bibfile, 'w') as bibtex :
        bibtex.write(filedata)




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
    parser_tex.add_argument('--journals', dest='journals', help="Replace known journal abbreviations", default=True, action='store_true')
    parser_tex.add_argument('--updatepublished', dest='updatepublished', help="Replace ADS arxiv entries in .tex file if published", default=True, action='store_true')
    parser_tex.set_defaults(func=fillbib_tex)

    parser_list = subparsers.add_parser("list", help="Create a bibliography given a list of ADS/iNSPIRE keys")
    parser_list.add_argument("keys", nargs="+", help="ADS/iNSPIRE keys to fetch")
    parser_list.set_defaults(func=fillbib_list)


    args = parser.parse_args()
    args.func(args)
    #try:
    #    args.func(args)
    #except:
    #    parser.print_usage()



