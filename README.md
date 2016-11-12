#filltex

Automatic queries to [ADS](http://adsabs.harvard.edu) and [INSPIRE](http://inspirehep.net) to get reference records. This is meant to be a tool for astronomers, physicists and mac users to improve your LaTex workflow. I did this mainly because I hate going to the [ADS](http://adsabs.harvard.edu) or [INSPIRE](http://inspirehep.net) websites and cut&paste citations manually. 


## Intro

What happens when you compile a LaTex file? How's bibliography handled?

  1. You first run `pdflatex` and all requested citation keys are dumped into a `.aux` file.
  2. You **should** have the required entries in you `.bib` file.
  3. Run `bibtex`, which looks for citations inside the `.bib` file and writes the results into a `.bbl`.
  4. Run `pdflatex` again, which processes the `.bbl` into the compiled paper, and dumps the citation records into `.aux`.
  5. Finally run `pdflatex` again, which puts the correct citation records into the paper.

The commands you need to run are: `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`. These, of course can be put into a script or a makefile and done in one goal.
Here I also want to automatically solve the second point: looking for citations on [ADS](http://adsabs.harvard.edu) (if you're an astronomer), [INSPIRE](http://inspirehep.net) (if you're a theoretical physicist) or both of them (if you still have to find your true identity like me).

So, here is the deal:

  - The `fillbib` python script queries both databases and create/update a `.bib` file without getting each record manually.
  - The `filltex` bash script put everything together to go from a `.tex` (and no `.bib`) into a `.pdf`.
  - I also provide [TexShop](http://pages.uoregon.edu/koch/texshop) engines for mac users

Of course, all of this works if your citations are specified in the [ADS](http://adsabs.harvard.edu) or [INSPIRE](http://inspirehep.net) format, e.g. `\cite{2016PhRvL.116f1102A}`, `\cite{Abbott:2016blz}`. If you use your personal keys `\cite{amazing_paper}`there's no way to get them from a database.


## Installation

Clone the reposotory and `cd` into your repo directory. Make the content of the `bin` directory executable

    chmod +x bin/*

and add it to your path
 
    PATH=$PATH:$(pwd)/bin
   
You can add this command to your `.bashrc`:
    
    echo "PATH=$PATH:$(pwd)/bin" >> ${HOME}/.bashrc
  
Finally, if you're a [TexShop](http://pages.uoregon.edu/koch/texshop) user and want to use this feature, run (might need sudo)

    cp filltex.engine ~/Library/TeXshop/Engines/filltex.engine
   
If you want to give it a try, you can run it on the `test.tex` file provided:
   
    cd test
    filltex test

and you should get a filled `.bib` file and a finished `.pdf`.
   
## Usage

### fillbib (script)

***`fillbib`*** looks for citations into a `.aux` file and create/update a `.bib` with the records foun on ADS and INSPIRE.
Usage:

    python fillbib.py precession <aux file> <bib file>

The second argument `<bib file>` can be omitted, and the code will scan the `.aux` file to guess the name of your bibliography file.
Arguments can be typed with or without extension, and the script is smart enough to figure it out. 
You need to have `.aux` file already, not just the `.tex`. If you don't have it, run `pdflatex` once.

### filltex (script)

***`filltex`*** does the whole thing: compile LaTex, fill the bibliography and gives you a `.pdf`. Usage:

    filltex <tex file>

Argument can be with or without extension, and the script is smart enough to figure it out. 

Since ADS bibliography items contains journal abbreviations, you need to use `aas_macros.sty` (available [here](http://doc.adsabs.harvard.edu/abs_doc/aas_macros.sty)). Don't worry, you just put `\include{aas_macros}` in your `.tex` file, and `filltex` would download the file for you if you need it.

At the end, `filltex` also runs [TexCount](http://app.uio.no/ifi/texcount) which counts the words in your document.

### TexShop

I use the [TexShop](http://pages.uoregon.edu/koch/texshop) editor, so I wrote an implementation of `filltex` for it. If you copied the `filltex.engine` file as specified above, just open your paper with [TexShop](http://pages.uoregon.edu/koch/texshop) and select ***filltex*** from the drop menu on the left. Now automagically compile your paper with `Typeset` or cmd-T. The [TexShop](http://pages.uoregon.edu/koch/texshop) engine will work only if the path is updated in your `.bashrc`, see above. 


### Test 

A short `text.tex` file is provided, where you can test this new way of writing papers!


## Known limitations

  - Treating eprints with ADS is tricky. When an eprint gets published they change the database key, but make the old key pointing to the new version! For instance, the key switches from `2016arXiv160203837T` to `2016PhRvL.116f1102A`.  If you're citing a prepreint which is not yet published, everything is fine: only the arXiv key (e.g. `2016arXiv160203837T`) is available and your reference list will show the arXiv version. If you're citing a paper that is published, both the eprint key (e.g. `2016arXiv160203837T`) and the published-version key (e.g. `2016PhRvL.116f1102A`) are available. If used, they will both point to the same published version! If you have a paper with citations to both, this will cause the same record to appear twice in the reference list (see teh test file). To avoid the issue, always use the published-paper key if a published version is out. INSPIRE doesn't have this problem, because they don't change the cite key when a paper gets published.

  - Multiple bibliographies are not allowed, only one `.bib` file per paper. I don't plan to implement multiple bibliographies in here, because you're not going to need them with this script: one paper, one bibliography, that's all.



## Credits
The code is developed and maintained by [Davide Gerosa](www.davidegerosa.com).
Please, report bugs to

    dgerosa@caltech.edu

The idea started from this `python` course taught by Michele Vallisneri at Caltech (and in particular from [this example](http://www.vallis.org/salon/summary-2.html)). The [TexCount](http://app.uio.no/ifi/texcount) code is developed by Einar Andreas Rodland. Useful info on the INSPIRE API are available [here](https://inspirehep.net/info/hep/pub_list)

