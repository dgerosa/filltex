# filltex

#### Automatic queries to ADS and INSPIRE databases to fill LaTex bibliography

`filltex` is a simple tool to fill LaTex reference lists with records from the [ADS](http://adsabs.harvard.edu) and [INSPIRE](http://inspirehep.net)  databases. [ADS](http://adsabs.harvard.edu) and [INSPIRE](http://inspirehep.net) are the most common databases used among the astronomy and theoretical physics scientific communities, respectively. `filltex` automatically looks for all citation labels present in a tex document and, by means of web-scraping, downloads  all the required citation records from either of the two databases. `filltex` significantly speeds up the LaTex scientific writing workflow, as all required actions (compile the tex file, fill the bibliography, compile the bibliography, compile the tex file again) are automated in a single command. We also provide an integration of `filltex` for the macos LaTex editor [TexShop](http://pages.uoregon.edu/koch/texshop).

If you use `filltex` for your research, please drop a citation to [this paper](http://joss.theoj.org/papers/10.21105/joss.00222):

- *filltex: Automatic queries to ADS and INSPIRE databases to fill LaTex bibliography*,
Davide Gerosa, Michele Vallisneri, The Journal of Open Source Software 2 (2017) 13.

Of course, you can use `filltex` to cite `filltex`! Just put `\cite{2017JOSS....2..222G}` in your tex file!

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.596848.svg)](https://doi.org/10.5281/zenodo.596848)


## Installation

`filltex` can be installed from the python package index [Pypi](https://pypi.python.org/pypi):
    
    pip install filltex

If you're a [TexShop](http://pages.uoregon.edu/koch/texshop) user and want to use this feature, run

    filltex install-texshop

<!-- The script requires the program `realpath`. This should be there by default on most linux distributions. On mac, you can get if from [Homebrew](http://brew.sh/)-->
<!--   brew install coreutils -->

If you want to give it a try, you can run it on the `example.tex` file provided in this repository:

    git clone https://github.com/dgerosa/filltex.git
    cd filltex/example
    filltex example

and you should get a filled `.bib` file and a finished `.pdf`.

## What's about?

What happens when you compile a LaTex file? How's bibliography handled?

  1. Run `pdflatex` and all requested citation keys are dumped into a `.aux` file.
  2. You **should** have the required entries in you `.bib` file.
  3. Run `bibtex`, which looks for citations inside the `.bib` file and writes the results into a `.bbl`.
  4. Run `pdflatex` again, which processes the `.bbl` into the compiled paper, and dumps the citation records into `.aux`.
  5. Finally run `pdflatex` again, which puts the correct citation records into the paper.

The commands you need to run are: `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`. These, of course can be put into a script or a makefile and done in one goal.
`filltex` is meant to automatically solve the second point as well: look for citations on [ADS](http://adsabs.harvard.edu), [INSPIRE](http://inspirehep.net) or both.

So, here is the deal:

  - The `fillbib` python script queries both databases and creates/updates a `.bib` file without getting each record manually.
  - The `filltex` bash script puts everything together to go from a `.tex` (and no `.bib`) into a `.pdf`.
  - I also provide [TexShop](http://pages.uoregon.edu/koch/texshop) engines for mac users

Of course, all of this works if your citations are specified in the [ADS](http://adsabs.harvard.edu) or [INSPIRE](http://inspirehep.net) format, e.g. `\cite{2016PhRvL.116f1102A}`, `\cite{Abbott:2016blz}`. If you use your personal keys `\cite{amazing_paper}`there's no way to get them from a database.

## Usage

### fillbib (script)

***`fillbib`*** has two working modes. It can either look for citations into a `.aux` file and create/update a bibtex file with the records found on ADS and INSPIRE, or it can fetch a list of bibtex entries specified from the command line from ADS or INSPIRE.

The first argument specifies the subcommand to run.

* `tex` will produce a bibtex file given an `.aux` file
* `list` will print a bibtex file given a list of keys from CLI

The help for the two subcommands can be obtained with

    fillbib.py {tex,list} --help

When working in `tex` mode it is possible to specify the name of the bibtex file using the option `--bibtex`. Otherwise, the code will scan the `.aux` file to guess the name of your bibliography file.  Arguments can be typed with or without extension, and the script is smart enough to figure it out. You need to have `.aux` file already, not just the `.tex`. If you don't have it, run `pdflatex` once.

`fillbib.py` contains two short unit tests, to make sure the web-scarping part is done correctly. You can run them from the `filltex` directiory using

    python
    > import fillbib
    > fillbib.test_ads()
    > fillbib.test_inspire()

or simply using [`pytest`](https://docs.pytest.org/en/latest/contents.html#toc)

    pytest fillbib
    
`fillbib` supports both python 2 (2.6 or higher) and python 3.

### filltex (script)

***`filltex`*** does the whole thing: compiles LaTex, fills the bibliography and gives you the final `.pdf`. Usage:

    filltex <tex file>

Argument can be with or without extension, and the script is smart enough to figure it out.


The script will replace some journal name with their [ISO4](https://en.wikipedia.org/wiki/ISO_4) abbreviations. You can disable this with the `journals` flag. Please send me pull requests with new journals that should be added here! ADS bibliography items contain some journal macros, which are also replaced in favour of ISO4. If you disable the ISO4 conversion, you'll need to use [`aas_macros.sty`](http://doc.adsabs.harvard.edu/abs_doc/aas_macros.sty).

By default, the script will also change your `.tex` file if an ADS arXiv entry has been published (see below). You can disable this by turning off `updatepublished`, see the help page.  

At the end, `filltex` also runs [TexCount](http://app.uio.no/ifi/texcount) which counts the words in your document. 

### ADS token

*This is optional but strongly recommended.* The ADS API has a daily request limit, and with this script you might hit it quickly. You should create an account on [ADS](http://adsabs.harvard.edu), then go to `Settings`, then `API Token`, and generate a token. Copy that string into an environment variable called `ADS_TOKEN` and make it system-wide available. The easiest way is to add the following to your `.bashrc` file:

```export ADS_TOKEN=....```

`filltex` will check if a token is available and use it. If not, it will default back to a simpler scraping implementation.

### TexShop

I use the [TexShop](http://pages.uoregon.edu/koch/texshop) editor, so I wrote an implementation of `filltex` for it. If you copied the `filltex.engine` file as specified above, just open your paper with [TexShop](http://pages.uoregon.edu/koch/texshop) and select ***filltex*** from the drop menu on the left. Now automagically compile your paper with `Typeset` or cmd-T. 
<!-- The [TexShop](http://pages.uoregon.edu/koch/texshop) engine will work only if the path is updated in your `.bashrc`, see above. -->

### Example

A short `example.tex` file is provided, where you can try this new way of writing papers!

## More details

  - Treating arXiv e-prints with ADS is tricky. When an e-print gets published they change the database key, but make the old key point to the new version! For instance, the key switches from `2016arXiv160203837T` to `2016PhRvL.116f1102A`.  If you're citing an e-print which is not yet published, everything is fine: only the arXiv key (e.g. `2016arXiv160203837T`) is available and your reference list will show the arXiv version. If you're citing a paper that is published, both the e-print key (e.g. `2016arXiv160203837T`) and the published-version key (e.g. `2016PhRvL.116f1102A`) are available. When used, they will both point to the same published version! If you write a document with citations to both, this will cause the same record to appear twice in your reference list (see the example file). To avoid the issue, `filltex` tries to update the pre-print key in your tex file if it finds a new version. In general, always use the published-paper key if a published version is out. INSPIRE doesn't have this problem, because they don't change the citation key when a paper gets published.

  - Multiple bibliographies are not allowed, only one `.bib` file per paper. I don't plan to implement multiple bibliographies in here, because you're not going to need them with this script: one paper, one bibliography, that's all.


### Manual installation from repository

If you don't like pip (but why wouldn't you?), you can install the code manually:

    git clone https://github.com/dgerosa/filltex.git # Clone repo
    cd filltex
    chmod +x bin/* # Make bin content executable
    PATH=$PATH:$(pwd)/bin # Add bin directory to path
    echo "PATH=$PATH:$(pwd)/bin" >> ${HOME}/.bashrc # To add the new path to your .bashrc    
    cp filltex.engine ~/Library/TeXshop/Engines/filltex.engine # To install the Texshop engine

`filltex` uses [TexCount](http://app.uio.no/ifi/texcount), which is included in most Tex distribution. In case it's not in yours, [here](http://app.uio.no/ifi/texcount/faq.html#setup) you can find installation instruction.

## References to filltex

  - `filltex` is included in the [suggested tools](https://inspirehep.net/info/hep/tools/index) from the INSPIRE team.
  - `filltex` is included the [official v3.80 release](http://pages.uoregon.edu/koch/texshop/changes_3.html) of Texshop.


## Credits
The code is developed and maintained by [Davide Gerosa](www.davidegerosa.com). If you find bugs, want to contribute to this project (any help is welcome!) or need help with it, just open an issue here on GitHub.

The idea started from [this](http://www.vallis.org/salon/) `python` course taught by [Michele Vallisneri](http://www.vallis.org/) at Caltech (and in particular from [this example](http://www.vallis.org/salon/summary-2.html)) and was later developed with key contributions from [David Radice](https://github.com/dradice). We also thank [Lars Holm Nielsen](https://github.com/lnielsen), reviewer for [The Journal of Open Software](http://joss.theoj.org/), for several suggestions which improved `filltex`. [TexCount](http://app.uio.no/ifi/texcount) is developed by Einar Andreas Rodland. Useful info on the INSPIRE and ADS APIs are available [here](https://inspirehep.net/info/hep/pub_list) and [here](https://github.com/adsabs/adsabs-dev-api).

## Changes
**v1.0**: Initial release, main functionalities.

**v1.1**: Version accepted in JOSS.

**v1.2**: Uploaded on pip.

**v1.3**: Compatible with new ADS "Bumblebee".

**v1.4**: Compatible with new INSPIRE API.

**v1.5**: New `tex` and `list` subcommands.

**v1.7**: New treatment of journal names, converting to ISO4 when available.




