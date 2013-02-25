BNC database and word frequency lists
Adam Kilgarriff

This file describes assorted frequency lists and related documentation for the
British National Corpus (BNC), to be found on this website.

The files are:

    a bibliographical database
    a lemmatised frequency list (various formats)
    unlemmatised, or 'raw', frequency lists (various formats)
    variances of word frequencies 

For a list and brief descriptions of CLAWS POS-tags, see here.

Bibliographical database

This gives bibliographical specifications of the 4124 files in the BNC, in a
one-line-per format (described in full in the first part of the file). Filename:
bib-dbase. Click here.

Lemmatised list

There is a lemmatised frequency list for the 6,318 words with more than 800
occurrences in the whole 100M-word BNC. The definition of a 'word' approximates
to a headword in an EFL dictionary such as Longman's Dictionary of Contemporary
English: so, eg, nominal and verbal "help" are listed separately, and the count
for verbal "help" is the sum of counts for verbal 'help', 'helps', 'helping',
'helped'.

The lemmatised list is called 'lemma' and is available in four forms: ordered
alphabetically or by frequency, and compressed (using gzip) or uncompressed, so
the four files are:

    lemma.al (124 KB)
    lemma.al.gz (55 KB)
    lemma.num (124 KB)
    lemma.num.gz (55 KB) 

The format for the list is:

        sort-order, frequency, word, word-class

and a sample from the top of the alphabetically-ordered list is:

	5 2186369 a det
	2107 4249 abandon v
	5204 1110 abbey n
	966 10468 ability n
	321 30454 able a

The list-creation process replicated that used at Longman for marking dictionary
frequencies in LDOCE 3rd edition, a process described in

    Kilgarriff, A. Putting Frequencies in the Dictionary. International Journal
    of Lexicography 10 (2) 1997. Pp 135--155. Available here.

Numbers, names, and items that would usually be capitalised are excluded. Only
simple words (eg containing no spaces) were considered. The following set of
word classes is used:

	conj (conjunction)            34 items
	adv  (adverb)                427
	v    (verb)                 1281
	det  (determiner)             47
	pron (pronoun)                46
	interjection                  13
	a    (adjective)            1124
	n    (noun)                 3262
	prep (preposition)            71
	modal                         12
	infinitive-marker              1

A word like "right" has four list entries, for adjective, adverb, interjection
and noun. (Just ten words have more than three list entries.)

Unlike the Longman list, only the BNC was used (so the lists only reflect
British, not American, frequencies); spoken and written frequencies are not
separated; spelling variants are not counted as a single word; manual checking
was less extensive. The lemmatised list was generated from the unlemmatised
lists which are thus a less theory-dependent form of data.

Unlemmatised lists
These are all available in 6 forms:

sorted alphabetically ("al") or by frequency (highest frequency first) ("num");
the complete lists, or a smaller file containing only those items occurring over
five times (suffix "o5"); all lists are available compressed using gzip
(".gz"). The o5 lists are also available uncompressed (no suffix). The
frequencies are for <CLAWS-word, POS> pairs. NB some CLAWS words - eg "in spite
of" are not orthographic words, while others are numbers etc, and some POS's are
CLAWS 'portmanteau tags', eg NN1-VVB, where CLAWS was uncertain as to whether
the word was a singular common noun or base form of a verb. See BNC manual for
serious documentation, also my "Putting frequencies in the dictionary" (see
above).

For a list and brief descriptions of CLAWS POS-tags, see here.

The format is: four fields, separated by spaces.

	1: frequency
	2: word
	3: pos
	4: number of files the word occurs in

For non-orthographic words, spaces are replaced by underscore, giving eg "in_spite_of".

Lists are provided for the complete BNC (all), and for three subsets, as below:

	cg	'context-governed' spoken material    
		(eg meetings, lectures etc)  6.2M tokens,  79,906 types
	demog  	'demographic' spoken material        
		(eg conversation)	     4.2M tokens,  54,652 types
        written                             89.7M tokens, 921,074 types
	all 	                           100.1M tokens, 939,028 types

File sizes in MB ("al" and "num" variants all the same size) are:

		all uncompressed	.gz	o5	o5.gz
-------------------------------------------------------------
all		18.1			4.8	4.0	1.32
cg		 1.4			0.39	0.43	0.15
demog		 0.9			0.26	0.25	0.09	
written		17.8			4.7	3.9	1.30
-------------------------------------------------------------

For all.al.gz click here
For all.al.o5 click here
For all.al.o5.gz click here
For all.num.gz click here
For all.num.o5 click here
For all.num.o5.gz click here
For written.al.gz click here
For written.al.o5 click here
For written.al.o5.gz click here
For written.num.gz click here
For written.num.o5 click here
For written.num.o5.gz click here
For cg.al.gz click here
For cg.al.o5 click here
For cg.al.o5.gz click here
For cg.num.gz click here
For cg.num.o5 click here
For cg.num.o5.gz click here
For demog.al.gz click here
For demog.al.o5 click here
For demog.al.o5.gz click here
For demog.num.gz click here
For demog.num.o5 click here
For demog.num.o5.gz click here
Variances

It has long been noted that corpus frequencies, taken alone, give a very limited
picture of a word's distribution in a corpus. As well as varying in raw
frequency, words vary in the extent to which they are equally spread across the
documents on the corpus. This 'burstiness' can be measured in a variety of ways
(Church and Gale, "Poisson Mixtures", JNLE 1(2), 1996). One straightforward
possibility is to take a large number of documents, all of the same length;
count the frequency of a word in each of these documents; and calculate the
(mean and) variance of this frequency.

The file presents the results of such an exercise. It is potentially of interest
for various statistical approaches to text processing (e.g. as author
identification and information retrieval) as well as for linguistic studies of
how much semantic content different English words have.

Method

The first 5,000 words of all documents (=files) longer than 5,000 words in the
written part of the BNC were taken. There were 2018 of these, so the subcorpus
was slightly over 10M words. (I used written-only on the premise that the spoken
material would be too different to usefully treat as part of the same population
- of course, one might say this about all sorts of subcorpora, but never mind.)
A frequency list was produced for each of these (truncated) documents. Then,
taking the 8189 word-pos pairs occurring 100 times or more in the sample, a
2018x8189 table giving the frequency of each word in each document was
produced. For each word, the mean and variance was calculated. There were two
ways to calculate mean and variance: including the zeros (eg always dividing by
2018) or excluding them (dividing by the number of documents the word occurred
in). For most purposes, it is the former that is of interest so this is what I
present. The "exclusive" figures may readily be reconstructed.

File format
Columns are

(1)     Word            )Using BNC definitions of 'word' and tags
(2)     POS-tag         ) - see IJL paper (details above)
(3)     Total freq (in 10M corpus)
(4)     (Truncated) documents that word-pos pair occurs in (out of 2018)
(5)     Mean (= Total freq./2018)
(6)     Variance
(7)     Variance/mean

The last is useful because, for distributions like the normal, poisson,
binomial, variance increases with mean, so, to make the variance figures
comparable for words of different base frequency, it is necessary to normalise
by the mean. This is the figure that shows that, e.g., pronouns have very high
variability, and prepositions, low (cf. Kucera and Francis 1982). Words are
presented in frequency order. The file is 400 KB (uncompressed) and 100 KB
(compressed).

Uncompressed, available here.
Compressed, available here.

This page: http://www.kilgarriff.co.uk/bnc-readme.html
Written: 20 Nov 1995
Updated: 15 March 1996
HTML version: 3 Nov 1998
Moved to http://www.kilgarriff.co.uk website: 1 Mar 2006
