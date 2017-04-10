#!/bin/bash
# Full tex compiler: run pdflatex, bibtex, query ADS and INSPIRE for citations and count words
# Davide Gerosa

SCRIPT=`realpath $0`
SCRIPT_LOCATION=`dirname $SCRIPT`


START=$PWD #Where you started

if [ ! -f ${START}/${1%.*}.tex ]; then
  echo "File not found!"
  exit 1
fi
FILE=${1%.*}
echo "filltex is compiling ${FILE}.tex"

# Get the journal abbreviations from ADS
if grep -q 'aas_macros' ${FILE}.tex; then # check if you need them
  if [ ! -f 'aas_macros.sty' ]; then
    curl -s 'http://doc.adsabs.harvard.edu/abs_doc/aas_macros.sty' > 'aas_macros.sty'
  fi
fi

# The pdflatex command return 0 if everyting is ok, or 1 if he get an error. If there's an error, I want the script to exit.
pdflatex --synctex=1 -halt-on-error ${FILE}.tex
[[ $? -eq 1 ]] && echo "pdflatex got an error" && exit

# Fill the bib fil with the ADS and INSPIRE references.
python ${SCRIPT_LOCATION}/fillbib.py "${FILE}"

# Fill the bbl file from the bib file
for file in *.aux ; do
    bibtex $file
done

pdflatex --synctex=1 -halt-on-error ${FILE}.tex
[[ $? -eq 1 ]] && echo "pdflatex got an error" && exit

pdflatex --synctex=1 -halt-on-error ${FILE}.tex
[[ $? -eq 1 ]] && echo "pdflatex got an error" && exit

# Count the words
perl ${SCRIPT_LOCATION}/texcount.pl "${FILE}".tex

# open the pdf file if you like
#open "${FILE}".pdf
