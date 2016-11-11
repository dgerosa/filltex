#filltex

Tools for astronomers, physicists and mac users to improve your LaTex workflow.  I did this mainly because I hate going to the ADS or INSPIRE databases and cut&paste citations manually.


## Intro

What happens when you compile a LaTex file? How's bibliography handled?

  1. You first run `pdflatex` and all requested citations keys are dumped into an `.aux` file.
  2. You **should** have the required entries in you `.bib` file.
  3. Run `bibtex`, which looks for citations inside the `.bib` file, and writes the results into a `.bbl`.
  4. Run `latex` again, which processes the `.bbl` into the compiled paper, and dumps the citation records into `.aux`.
  5. Finally run `latex` again, which puts the correct citation records into the paper.

The commands you need to run are: `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`. These, of course can be put into a script or a makefile and done in one goal.
Here we also want to automatically solve the second point: looking for citations on [ADS](http://adsabs.harvard.edu) (if you're an astronomer), [INSPIRE](http://inspirehep.net) (if you're a theoretical physicists) or both of them (if you do gravitational waves).

So, here is the deal:

  - The `fillbib` python script queries both databases and create/update a `.bib` file without getting each record manually.
  - The `filltex` bash script put everything together to go from a `.tex` (and no `.bib`) into a `.pdf`.
  - I also provide TexShop engines for mac users

Of course, all of this works if your citations are specified in the ADS or INSPIRE format, e.g. `\cite{2016PhRvL.116f1102A}`, `\cite{Abbott:2016blz}`. If you use your personal keys there's no way to get them from the databases.


## Installation

Clone the reposotory and `cd` into your repo directory. Make the content of the `bin` directory executable

    chmod +x bin/*

and add it to your path
 
    PATH=$PATH:~/REPO_DIRECTORY/bin
   
You may want to add this command to your `.bashrc` to avoid repeating it
    
    echo "PATH=$PATH:~/REPO_DIRECTORY/bin" >> ${HOME}/.bashrc
  
Finally, if you're a [TexShop](http://pages.uoregon.edu/koch/texshop) user and want to use this features, copy

    cp filltex.engine ~/Library/TeXshop/Engines/filltex.engine
   
This will work only if the path is updated in your `.bashrc`, see above. You might need to sudo the above command.

   
## Usage

### fillbib (script)

***`fillbib`*** looks for citations into a `.aux` file and create/update a `.bib` with the records foun on ADS and INSPIRE.
Usage:

    python fillbib.py precession <aux file> <bib file>

The second argument `<bib file>` can be omitted, and the code will scan the `.aux` file to guess the name of your bibliography file.
Arguments can be with or without extension, and the script is smart enough to figure it out. 
You need the `.aux` file already. If you don't have it, run `pdflatex` once.

### filltex (script)

***`filltex`*** the whole thing: compile latex, fill the bibliography and gives you a pdf. Usage:

    filltex <tex file>

Argument can be with or without extension, and the script is smart enough to figure it out. 

Since ADS bibliography items contains journal abbreviations, you need to use `aas_macros.sty` (available [here](http://doc.adsabs.harvard.edu/abs_doc/aas_macros.sty)). Don't worry, you just put `\include{aas_macros}` in your `.tex` file, and `filltex` would get the file for you. 

At the end, `filltex` also runs [TexCount](http://app.uio.no/ifi/texcount) which counts the words in your document.

### TexShop

I use the TexShop editor, so I wrote an implementation of `filltex` into it. If you copied the `filltex.engine` file as written above, just open your paper with TexShop and select ***filltex*** from the menu on the left. Now automagically compile your paper with `Typeset` or cmd-T.

## Known limitations

  - Treating eprints with ADS is tricky because when an eprint gets published they change the database key! For instance, it switches from `2016arXiv160203837T` to `2016PhRvL.116f1102A`.  If you're citing a prepreint which is not yes published, everything is fine: only the arxiv key (e.g. `2016arXiv160203837T`) is available and your reference list will show the arXiv version. If you're citing a paper that is published, both the key for the arxiv version (e.g. `2016arXiv160203837T`) and the key for the published version (e.g. `2016PhRvL.116f1102A`) will point to the published version! If you have a paper with citations to both, they will be treated as two identical records and the same reference will appear twice in the list. To avoid the issue, always use the published-paper key if a published version is indexed in ADS. INSPIRE doesn't have this problem, because they don't change the cite key when a paper get published.


  - Multiple bibliographies are not allowed, only one `.bib` file per paper. I don't plan to implement multiple bibliographies, because you're not going to need them with this script: one paper, one bibliography.



### Credits
The code is developed and maintained by [Davide Gerosa](www.davidegerosa.com).
Please, report bugs to

    dgerosa@caltech.edu

The idea started from this `python` course taught by Michele Vallisneri at Caltech (and in particular from [this example](http://www.vallis.org/salon/summary-2.html)). The [TexCount](http://app.uio.no/ifi/texcount) code is developed by Einar Andreas Rodland. Useful info on the INSPIRE API are available [here](https://inspirehep.net/info/hep/pub_list)

