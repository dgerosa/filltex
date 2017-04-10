# filltex

 `filltex` is a simple tool to fill LaTex reference lists with records from the [ADS](http://adsabs.harvard.edu) and [INSPIRE](http://inspirehep.net)  databases. [ADS](http://adsabs.harvard.edu) and [INSPIRE](http://inspirehep.net) are the most common databases used among the theoretical physics and astronomy scientific communities, respectively. `filltex` automatically looks for all citation labels present in a tex document and, by means of web-scraping, downloads  all the required citation records from either of the two databases. `filltex` significantly speeds up the LaTex scientific writing workflow, as all required actions (compile the tex file, fill the bibliography, compile the bibliography, compile the tex file again) are automated in a single command. We also provide an integration of `filltex` for the macos LaTex editor [TexShop](http://pages.uoregon.edu/koch/texshop).

If you use `filltex` for your paper, consider dropping a citation in the acknowledgemens.

[![DOI](https://zenodo.org/badge/73505895.svg)](https://zenodo.org/badge/latestdoi/73505895)

## Intro

What happens when you compile a LaTex file? How's bibliography handled?

  1. Run `pdflatex` and all requested citation keys are dumped into a `.aux` file.
  2. You **should** have the required entries in you `.bib` file.
  3. Run `bibtex`, which looks for citations inside the `.bib` file and writes the results into a `.bbl`.
  4. Run `pdflatex` again, which processes the `.bbl` into the compiled paper, and dumps the citation records into `.aux`.
  5. Finally run `pdflatex` again, which puts the correct citation records into the paper.

The commands you need to run are: `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`. These, of course can be put into a script or a makefile and done in one goal.
`filltex` is meant to automatically solve the second point as well: look for citations on [ADS](http://adsabs.harvard.edu), [INSPIRE](http://inspirehep.net) or both.

So, here is the deal:

  - The `fillbib` python script queries both databases and create/update a `.bib` file without getting each record manually.
  - The `filltex` bash script put everything together to go from a `.tex` (and no `.bib`) into a `.pdf`.
  - I also provide [TexShop](http://pages.uoregon.edu/koch/texshop) engines for mac users

Of course, all of this works if your citations are specified in the [ADS](http://adsabs.harvard.edu) or [INSPIRE](http://inspirehep.net) format, e.g. `\cite{2016PhRvL.116f1102A}`, `\cite{Abbott:2016blz}`. If you use your personal keys `\cite{amazing_paper}`there's no way to get them from a database.


## Installation

Clone the repository

    git clone https://github.com/dgerosa/filltex.git

and `cd` into your repo directory

    cd filltex

My script requires the program `realpath`. This should be there by default on most linux distributions. On mac, you can get if from [Homebrew](http://brew.sh/)

    brew install coreutils

Now, make the content of the `bin` directory executable

    chmod +x bin/*

and add it to your path

    PATH=$PATH:$(pwd)/bin

You can add this command to your `.bashrc`:

    echo "PATH=$PATH:$(pwd)/bin" >> ${HOME}/.bashrc

Finally, if you're a [TexShop](http://pages.uoregon.edu/koch/texshop) user and want to use this feature, run (might need sudo)

    cp filltex.engine ~/Library/TeXshop/Engines/filltex.engine

If you want to give it a try, you can run it on the `example.tex` file provided:

    cd example
    filltex example

and you should get a filled `.bib` file and a finished `.pdf`.

## Usage

### fillbib (script)

***`fillbib`*** looks for citations into a `.aux` file and create/update a `.bib` with the records found on ADS and INSPIRE.
Usage:

    python fillbib.py <aux file> <bib file>

The second argument `<bib file>` can be omitted, and the code will scan the `.aux` file to guess the name of your bibliography file.
Arguments can be typed with or without extension, and the script is smart enough to figure it out.
You need to have `.aux` file already, not just the `.tex`. If you don't have it, run `pdflatex` once.

`fillbib` contains two short unit tests, to make sure the web-scarping part is done correctly. You can run them from the `filltex` directiory using

    python
    > import fillbib
    > fillbib.test_ads()
    > fillbib.test_inspire()

or simply using [`pytest`](https://docs.pytest.org/en/latest/contents.html#toc)

    pytest fillbib

### filltex (script)

***`filltex`*** does the whole thing: compile LaTex, fill the bibliography and gives you the final `.pdf`. Usage:

    filltex <tex file>

Argument can be with or without extension, and the script is smart enough to figure it out.

Since ADS bibliography items contains journal abbreviations, you need to use `aas_macros.sty` (available [here](http://doc.adsabs.harvard.edu/abs_doc/aas_macros.sty)). Don't worry, you just put `\include{aas_macros}` in your `.tex` file, and `filltex` would download the file for you if you need it.

At the end, `filltex` also runs [TexCount](http://app.uio.no/ifi/texcount) which counts the words in your document. 

### TexShop

I use the [TexShop](http://pages.uoregon.edu/koch/texshop) editor, so I wrote an implementation of `filltex` for it. If you copied the `filltex.engine` file as specified above, just open your paper with [TexShop](http://pages.uoregon.edu/koch/texshop) and select ***filltex*** from the drop menu on the left. Now automagically compile your paper with `Typeset` or cmd-T. The [TexShop](http://pages.uoregon.edu/koch/texshop) engine will work only if the path is updated in your `.bashrc`, see above.


### Example

A short `example.tex` file is provided, where you can try this new way of writing papers!


## Known limitations

  - Treating arXiv e-prints with ADS is tricky. When an e-print gets published they change the database key, but make the old key point to the new version! For instance, the key switches from `2016arXiv160203837T` to `2016PhRvL.116f1102A`.  If you're citing an e-print which is not yet published, everything is fine: only the arXiv key (e.g. `2016arXiv160203837T`) is available and your reference list will show the arXiv version. If you're citing a paper that is published, both the e-print key (e.g. `2016arXiv160203837T`) and the published-version key (e.g. `2016PhRvL.116f1102A`) are available. When used, they will both point to the same published version! If you write a document with citations to both, this will cause the same record to appear twice in your reference list (see the example file). To avoid the issue, always use the published-paper key if a published version is out. INSPIRE doesn't have this problem, because they don't change the citation key when a paper gets published.

  - Multiple bibliographies are not allowed, only one `.bib` file per paper. I don't plan to implement multiple bibliographies in here, because you're not going to need them with this script: one paper, one bibliography, that's all.



## Credits
The code is developed and maintained by [Davide Gerosa](www.davidegerosa.com). If you find bugs, want to contribute to this project (any help is welcome!) or need help with it, just open an issue here on GitHub. For anything else, feel free to drop me an email:

    dgerosa@caltech.edu

The idea started from [this](http://www.vallis.org/salon/) `python` course taught by [Michele Vallisneri](http://www.vallis.org/) at Caltech (and in particular from [this example](http://www.vallis.org/salon/summary-2.html)). The [TexCount](http://app.uio.no/ifi/texcount) code is developed by Einar Andreas Rodland. [TexCount](http://app.uio.no/ifi/texcount) may be already included in your Tex distribution; in case it's not, you can find it in this repository for your convenience. Useful info on the INSPIRE and ADS APIs are available [here](https://inspirehep.net/info/hep/pub_list) and [here](https://github.com/adsabs/adsabs-dev-api).
