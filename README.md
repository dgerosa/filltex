#filltex

Tools for astronomers, physicists and mac users to improve your Latex workflow. 
I started this mainly because I hate going to the ADS or INSPIRE databases and cut&paste the bibliographic citations for each paper.


## Why

What happens when you compile a latex file? How's bibliography handled?

  1. You first run `latex` and all requested citations keys are dumped into an `.aux` file.
  2. You should have the required entries in you `.bib` file.
  3. Run `bibtex`, which looks for citations inside the `.bib` file, and writes the results into a `.bbl`.
  4. Run `latex` again, which processes the `.bbl` into the compiled paper, and dumps the citation records into `.aux`.
  5. Finally run `latex` again, which puts the correct citation records into the paper.

The commands you need to run are: pdflatex, bibtex, pdflatex, pdflatex. These, of course can be put into a bash script and done in one goal.
Here we also want to automatically solve the second point: looking for citations on [ADS](http://adsabs.harvard.edu) (if you're an astronomer), [INSPIRE](http://inspirehep.net) (if you're a theoretical physicists) or both of them (if you do gravitational waves).

So, here is the deal:

  - The `fillbib` python script queries both databases and create/update a `.bib` file without getting each record manually.
  - The `filltex` bash script put everything together to go from a `.tex` (and no `.bib`) into a `.pdf`.
  - I also provide TexShop engines for mac users

## Installation

Clone the reposotory and `cd` into your repo directory. Make the content of the `bin` directory executable

    chmod +x bin/*

and add it to your path
 
    PATH=$PATH:~/REPO_DIRECTORY/bin/
   
You may want to add this command to your `.bashrc` to avoid repeating it
    
    echo "PATH=$PATH:~/REPO_DIRECTORY/bin/" >> ${HOME}/.bashrc
   
   
## Script usage

***`fillbib`*** looks for citations into a `.aux` file and create/update a `.bib` with the records foun on ADS and INSPIRE.
Usage:

    python fillbib.py precession <aux file> <bib file>

The second argument `<bib file>` can be omitted, and the code will scan the `.aux` file to guess the name of your bibliography file.
Arguments can be with or without extension, and the script is smart enough to figure it out. 
You need the `.aux` file already. If you don't have it, run `pdflatex` once.

***`filltex`*** the whole thing: compile latex, fill the bibliography and gives you a pdf. Usage:

    filltex <tex file>

Argument can be with or without extension, and the script is smart enough to figure it out.



## Known limitations

  - Multiple bibliographies are not allowed, only one `.bib` file per paper. I don't plan to implement multiple bibliographies, because wth 





At the end, I'm also running a perl script\footnote{\url{http://app.uio.no/ifi/texcount/}} to count the words in each section: useful to write letters, reports...


\section{Really?}
Place the script directory somewhere \url{<your_location>} in your system; open \url{dtex.sh} and modify the first line with your chosen location.

Open the terminal, go into a directory where you keep your paper and run 
\url{bash <your_location>/dtex.sh}


You can use this file to test my script. First of all, remove everything  you may already have (aux, bib, bbl)  but this tex file.

This is a citation from ADS: \url{\cite{1975ApJ...195L..51H}} \cite{1975ApJ...195L..51H}

This is a citation from INSPIRE:\url{\cite{Hulse:1974eb}} \cite{Hulse:1974eb}




\cite{2008PhRvL.101p1101S}

\section{Known limitations}
\begin{enumerate}

\item Of course, computers are stupid. You must enter the cite keys in your tex file using the standard format used by the databases. You can't use your nicknames \url{\cite{awesome_paper}} but you must keep \url{\cite{1975ApJ...195L..51H}} or \url{\cite{Hulse:1974eb}}. ArXiv number are also fine \url{\cite{ gr-qc/0610154 | }} but they will be changed in the tex file to match the INSPIRE entry

\item Currently, the name of the bibliography file must be  the same as the one of the tex file you're running. I could change this, but I never bothered, because I just use a different bib for each different paper.

\item eprints in ADS are tricky. When an print get published they change the cite key, but keep the url. This means that if you have a old arXiv reference, my script will like to store it with a different records. I fixed this now: this is a published paper \cite{2010PhRvD..81h4054K} and this is its arXiv version \cite{2010arXiv1002.2643K}. It will appear twice in the bibliography, that's unavoidable because the script can't know that the paper is the same if it appears with two different (both allowed!) keys. INSPIRE doesn't have this problem, because they don't change the cite key when a paper get published.
\item I'd like to write an engine to do all of this from TexShop, which I like. I tried, but I've been unsuccessful so far. I still need a way to pass parameters.  

\end{enumerate}

\bibliography{test2}
\end{document}





**Author** Davide Gerosa

**email** dgerosa@caltech.edu


