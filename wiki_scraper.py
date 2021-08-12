import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords #getting stopwords
from collections import defaultdict
import re #regex 
import sys

'''
    This software uses Python 3.8.6
        Requests library
        BeautifulSoup4 Library
        NLTK
        re (built-in)
        collections (built-in)
        sys (built-in)
        
    in order to install do:
        python -m pip install requests beautifulsoup4 nltk
'''

#global constants
STOPWORDS = stopwords.words('english')
STOPWORDS.append('')



def get_title(soup: 'html.parser') -> str:
    '''
        input: html.text parsed with soup

        output: the Title of the wikipedia page
    '''
    return soup.find('h1').text

def get_sections(soup: 'html.parser') -> [(str,str)]:
    '''
        input: html.text parsed with soup

        output: a list of headings from a wikipedia page
    '''

    div = soup.find('div', {'class': 'toc'}) #finds table of contents section of wikipedia page
    list_a = div.find_all('a') #finds all of the headings inside of the table of contents page
    headings = []

    for i in list_a:
        #adds each individual heading and their section number
        headings.append( (i.get('href')[1:], i.find('span').text) ) 
    
    return headings

def print_headings(headings: [(int,int)]) -> 'print': 
    #given a list of headings, it prints it in an organized fashion
    for heading, num in headings:
        print('-'*len(num.split('.')) + f'> {num} {heading}')
    

def parse_body(body: 'html tag at level containing all body content', headings: (str,str) ) -> ({str:str},{str:[str]}):
    '''
    Description:
        Goes through every tag from the wikipedia body tag and then finds every p tag 
        (which contains the text of the paragraph under a heading) and puts it under a heading.

        there is no way wikipedia separates the p's, and li's for us to differentiate, so we go through every tag 
        and use the h tags that contain the heading names to differentiate from the texts in the webpage.


        input: 
            body: topmost tag that holds all p's and h's, and li  tags for wikipedia site
            headings: list of ordered tuple of headings with their numbers
        
        output: 
            --> a dictionary with a giant text associated with each individual heading
            --> a dictionary with a list of hyperlinks associated with each individual heading
    '''
    len_headings = len(headings)
    ctr = 0

    head_dict_text = defaultdict(str) #contains all text per headings
    head_dict_href = defaultdict(list) #contains all hyperlinks per headings

    for tag in body: #loop through all tags under body
        heading = headings[ctr][0]

        if tag.name == 'p':
            head_dict_text[heading] += tag.text.strip('\n').strip('.').strip('(').strip(')')
            for href in tag.find_all('a'): #find any hyperlinks and add to dictionary
                head_dict_href[heading].append( (href.text, href.get('href')) )

        if tag.name == 'ul': #makes sure to include bullet points in the texts.
            for li in tag.find_all('li'):
                    head_dict_text[heading] += li.text


        elif tag.name[0] == 'h': #each time it passes a heading, iterate to next index
            ctr+=1

    return (head_dict_text, head_dict_href)

def store_frequency_dict(strin: str) -> {str: int}:
    '''
        takes in a string and creates a dictionary that stores frequency of every word in string.
        it filters out the non-alphanumeric characters and then excludes stop words.

        input: string of words
        output: dictionary containing words and their frequencies
    '''
    list_str = strin.split()
    freq_words = defaultdict(int)
    
    for word in list_str:
        word = word.lower()
        word = re.sub(r'\W+', '', word) #remove punctuation and other non-alphanumeric characters that can ruin words
        if word not in STOPWORDS:
            freq_words[word] += 1

    return freq_words

def top_n(freq_words: {str:int}, n: int) -> [(str, int)]:
    '''
        takes in a dictionary of word frequencies and an integer n.
        sorts words frequencies by the most frequent and takes the top n words in terms of frequency

        input: 
            freq_words: dictionary of word frequencies
            n: integer of top "n" words

        output: top n words frequencies in a word frequency dictionary
    '''
    ls_freq = sorted(freq_words.items(), key=(lambda i: i[1]), reverse=True) #sort
    return ls_freq[:n]

if __name__ == '__main__':
    if len(sys.argv) == 2:
        test_url = sys.argv[1]
    else:
        print('Enter a URL')
        sys.exit()

    #use request library to parse url
    html_text = requests.get(test_url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    #store body tag for use in functions
    body = soup.find('div', {'class': 'mw-parser-output'})
    #filter the body tag for only the "p", "ul", and "h" that are contained inside.
    body = body.find_all(['p','ul','h','h2','h3','h4', 'h5', 'h6'],recursive=False)[1:]

    print('Organization of the Wikipedia Page')
    title = get_title(soup)
    headings = get_sections(soup)

    print(f'Title: {title}')
    print_headings(headings)
    print('\n\n')

    #include the title inside of headings
    headings.insert(0, (title,0) )
    texts_in_headings, hyperlinks_in_headings = parse_body(body, headings)

    #Iterating through headings to display hyperlinks and top n words
    print('Contents of Wikipedia Page')
    for heading, num in headings:
        print(f'{num} {heading}:\n')

        #hyperlink display
        hyperlinks = hyperlinks_in_headings[heading]
        if len(hyperlinks) != 0:
            print('  Hyperlinks: (text, url) ')
            for hyperlink in hyperlinks:
                print(f'    {hyperlink}')
        else:
            print('  No Hyperlinks')
        print('\n')

        
        #top n words display
        freq_dict = store_frequency_dict(texts_in_headings[heading])
        top_n_words = top_n(freq_dict, 5)
        if len(top_n_words) != 0:
            print('  Top 5 frequent words: ')
            for word, freq in top_n_words:
                print(f'    {word} -> {freq}')
            print('\n')

        print('\n')

