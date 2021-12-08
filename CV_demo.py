import operator
import sys
import fitz # if needed use: pip install PyMuPDF
import re
import metapy
import numpy as np

""" load_pdf: loads pdf file to parse with PyMuPDF/fitz
    input: pdf_filename; 
    output: pdf doc 
"""
def load_pdf(pdf_filename):
    doc = fitz.open(pdf_filename)
    return doc

""" load_stop_words: loads stopwords file """
def load_stop_words():    
    stop_words = set()
    with open("stops.txt", 'r', encoding="utf8") as f:
        for line in f:
            stop_words.add(str(line.strip()))
    return stop_words

""" load_transcript: loads transcript text file to parse
    input: transcript_filename; 
    output: string lecture of stripped transcript text  
"""
def load_transcript(transcript_filename):
    with open(transcript_filename, 'r') as f:
            lecture = str(f.readlines())
            lecture = re.sub(r"[^a-zA-Z0-9_ -]+", '', lecture).strip()
    return lecture

""" Each PDF has pages, and each page contains blocks.
    Each block has lines, and each line has spans.
    Spans contain text if the block type is 0.
    Spans contain text and font size and style.
    get_fonts: collects font information from the pdf doc 
    input: pdf doc; 
    outputs: sorted list font_counts (font size, count) regardless of font
             styles dict {[(font size, font)]: count} for each style 
"""
def get_fonts(doc):
    font_counts, styles = {}, {}
    for page in doc:    # for each page, get text data
        blocks = page.get_text("dict")["blocks"]          
        for b in blocks:    # for each block
            if b['type'] == 0:  # type 0 means a block contains text
                for l in b["lines"]:  # for each line
                    for s in l["spans"]:    # for each span, get fonts
                        s['size'] = round(s['size'])
                        font_counts[s['size']] = font_counts.get(s['size'], 0) + 1  # count the fonts usage
                        styles[(s['size'], s['font'])] = styles.get((s['size'], s['font']), 0) + 1
                        
    font_counts = sorted(font_counts.items(), key=operator.itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("No fonts found!")

    return font_counts, styles

""" Determine which styles are likely headings/important text.
    Headings are likely to contain important concepts of the lecture.
    find_headers: uses font data to select most likely header font styles
    input: font_counts, styles
    output: list header_styles which may contain concepts
"""
def find_headers(font_counts, styles):
    font_sizes, counts = map(list, zip(*font_counts))
    font_sizes.sort(reverse=True) # sorted list of font sizes

    # Paragraph text is often the size of the most frequently used text.
    # However, using this logic often generated too many irrelevant concepts.
    # So I made the threshold for the size of paragraph text larger.
    p_size = max([font_counts[0][0], max(font_sizes)*.75, np.mean(font_sizes)])

    # forbidden fonts mostly contain math text or symbols; not likely a concept
    forbidden_fonts = ('ArialMT','CambriaMath','Cambria Math','Cambria_Math',
                       'MT Extra', 'Symbol','SymbolMT','TimesNewRomanPSMT','Wingdings')
    
    header_styles = []
    # for each font style, if larger than the p_size threshold, add style to 
    # list of potential header_styles. 
    # Calibri Bold was often used for slide headings, so I've included all 
    # instances of this font, regardless of size.
    for style in styles:
        size, font = style
        if font not in forbidden_fonts: 
            if (size > p_size) or (font=='Calibri,Bold'):
                header_styles.append((size, font))

    return header_styles

""" Parse PDF text
    parse_doc: Uses header_styles to extract important text/concepts from PDF.
    input: pdf doc, header_styles
    output: list potential_concepts, list linksl (links contained in PDF)
"""

def parse_doc(doc, header_styles):
    potential_concepts = []
    first = True  
    linksl = set() 
    previous_s = {}

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        # collect link text to remove
        links = page.get_links()    
        for link in links:
            linksl.add(re.sub(r"[^a-zA-Z0-9_ -]+", '', link['uri']).strip())
        
        title = ""
        if blocks[0]['type']==0:
            # the 1st span/line/block on page typically contains slide title
            title = blocks[0]['lines'][0]['spans'][0]['text']
        for b in blocks:  # iterate through the text blocks
            # if the slide is an additional readings (references) slide
            # do not save the text as a concept
            if (b['type'] == 0) and ('Additional Reading' not in title):
                block_string = ""  # text from block
                for l in b["lines"]:  
                    for s in l["spans"]: 
                        s['size'] = round(s['size'])
                        if s['text'].strip():  # if span contains text
                            if first:
                                previous_s = s
                                first = False
                                # if font is a header style, keep text
                                if (s['size'], s['font']) in header_styles: block_string = s['text']

                            else:
                                if s['size'] == previous_s['size']:
                                    if (s['size'], s['font']) in header_styles:
                                        if block_string == "": block_string = s['text'] # new block
                                        else: block_string += " " + s['text'] # same block, concatenate text

                                else:
                                    if (s['size'], s['font']) in header_styles: block_string = s['text']

                            previous_s = s
                            
                    block_string += "\n"
                    if block_string:
                        B = block_string.split("\n")                         
                
                for string in B:
                    block_string = re.sub(r"[^a-zA-Z0-9_ -]+", '', string).strip()
                    if block_string: potential_concepts.append(block_string)

    return potential_concepts, linksl

''' get_concepts: filter potential concepts by stopwords, links and format
    input: potential_concepts, linksl, stop_words
    output: dict short_concepts {(trimmed concept): original concept}
            string concept_s of all words in concepts
'''
def get_concepts(potential_concepts, linksl, stop_words):
    short_concepts = {}
    concepts_s = ""
    for t in potential_concepts:
        s = ""
        # keep upper case concepts (usually main ideas/headings/titles)
        if (t[0].isupper()):
            for word in t.split():
                # remove stopwords and links
                if (word.lower() not in stop_words) and (word not in linksl):
                    s = s + word + " "
            if (len(s) > 0 and s[0].isupper()):
                short_concepts[s.strip()] = t.strip()
        concepts_s += s
    return short_concepts, concepts_s

''' get_grams: use MetApy to tokenize and generate uni, bi, & trigrams
    input: text string
    output: 3x dict: unigrams, bigram, trigrams {[gram]: count}
'''
def get_grams(text):
    doc = metapy.index.Document()
    doc.content(text)
    tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
    tok = metapy.analyzers.LowercaseFilter(tok)
    tok = metapy.analyzers.ListFilter(tok, "stops.txt", metapy.analyzers.ListFilter.Type.Reject)
    
    ana = metapy.analyzers.NGramWordAnalyzer(1, tok)
    grams = ana.analyze(doc)
    unigrams = {key:val for key, val in grams.items() if val >0}
    
    grams = {}
    ana = metapy.analyzers.NGramWordAnalyzer(2, tok)
    grams = ana.analyze(doc)
    bigrams = {key:val for key, val in grams.items() if val >0}
    
    grams = {}
    ana = metapy.analyzers.NGramWordAnalyzer(3, tok)
    grams = ana.analyze(doc)
    trigrams = {key:val for key, val in grams.items() if val >0}
    return unigrams, bigrams, trigrams

''' get_grams: gives arbitrary score to concepts for ranking output order
    input: lecture and concepts_s strings, and concepts matrix
    output: array scores of concepts
'''
def get_concept_score(lecture, concepts_s, concepts):
    doc_uni, doc_bi, doc_tri = get_grams(lecture)
    pdf_uni = get_grams(concepts_s)[0]
    concepts_list = concepts[:,0]
    scores = []
    
    for i in range(len(concepts_list)):
        content_uni, content_bi, content_tri = get_grams(concepts_list[i])
        x = 0

        for u in content_uni:
            if u in doc_uni.keys():
                x = x + doc_uni[u]/(sum(doc_uni.values()))

            if u in pdf_uni.keys():
                x = x + 2*((pdf_uni[u])/(sum(doc_uni.values())))
    
        for b in content_bi:
            if b in doc_bi.keys():
               x = x + 2*(doc_bi[b]/(sum(doc_bi.values())))
    
        for t in content_tri:
            if t in doc_tri.keys():
               x = x + 20*(doc_tri[t]/(sum(doc_tri.values())))
        
        scores.append(round(x, 2))
    
    scores = np.expand_dims(scores, axis=1)
    return scores

""" choose_output: selects concepts to output based on length and score """
def choose_output(concepts):
    num_concepts = len(concepts[:,0])
    
    output = ""
    for i in range(num_concepts):
        o = ""
        if float(concepts[i,2]) > 0:
            if len(concepts[i,0].split()) <=3: 
                o = concepts[i,1]
            if ((len(concepts[i,0].split()) >3) or (len(concepts[i,1].split()) > 6)): 
                o = concepts[i,0] 
        if o: output += o + ", "
    output = output[0:len(output)-2]
    return output

""" print_output: prints results """
def print_output(concepts, loop, file_number, output):
        print("Lecture "+str(file_number)+": ")
        print("Concepts Matrix")
        print(concepts)
        print("Selected Concepts")
        print(output)
        if loop: print("-----------------------------------------------------------------")
 
def main(loop, file_number):
        pdf_filename = "pdfs1/" + str(file_number) + ".pdf"
        transcript_filename = "transcripts1/" + str(file_number) + ".txt"
        # Load PDF doc
        doc = load_pdf(pdf_filename)   
        # Get PDF Fonts
        font_counts, styles = get_fonts(doc)
        # Identify potential PDF headings from font styles
        header_styles = find_headers(font_counts, styles)
        # Identify potential concepts from header styles
        potential_concepts, linksl = parse_doc(doc, header_styles)
        # Generate short concepts by filtering stopwords and links from (long) potential concepts         
        short_concepts, concepts_s = get_concepts(potential_concepts, linksl, load_stop_words()) 
        short_concepts_list = np.expand_dims(np.array(list(short_concepts.keys())), axis=1)
        long_concepts_list = np.expand_dims(np.array(list(short_concepts.values())), axis=1)
        # Create concepts matrix to hold both long and short versions of concepts
        concepts = np.concatenate((short_concepts_list, long_concepts_list), axis=1)
        # Load lecture text transcript file
        doc = metapy.index.Document()
        lecture = load_transcript(transcript_filename)
        # Calculate scores for concepts, add to concepts matrix
        c = get_concept_score(lecture, concepts_s, concepts)
        concepts = np.concatenate((concepts, c), axis=1)
        concepts = concepts[concepts[:,2].astype(float).argsort()][::-1]
        # Select final output and print results
        output = choose_output(concepts)
        print_output(concepts, loop, file_number, output)
    

def run_demo(loop=False, file_number=1):
    if loop == False:
        main(loop, file_number)  
    else:
        for i in range(1,6):
            main(loop, i)

if (len(sys.argv) >= 2):
    if sys.argv[1].lower() == 'loop': 
        run_demo(loop=True)
        quit()
        
    if (sys.argv[1] in ['1','2','3','4','5']): 
        run_demo(loop=False, file_number=sys.argv[1])
        quit()

    if (sys.argv[1]):
            print('!!! Invalid Entry !!!')
            print('... Running Default: Lecture 3 ... \n')

""" To run demo, run the code below with chosen file_number (1 to 5) """
run_demo(loop=False, file_number=3) # <------ set file_number (1:5)

""" To run a loop of all files, use the code below. 
    DemoOutput.txt contains results.
"""
#run_demo(loop=True)
