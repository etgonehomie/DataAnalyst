from bs4 import BeautifulSoup as bs    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from flashtext import KeywordProcessor # https://flashtext.readthedocs.io/en/latest/
import urllib.request
import ssl
from time import sleep
# CONSTANTS
SLEEP_SEC = 30
USER_ID_KEY = 'user_id'
DIRECTORY = "/Users/E1T5/Desktop/Personal/burma/"
YELP_BIZ_URL = "https://www.yelp.com/biz/"
BURMA_OAKLAND_URL = "burma-superstar-oakland-6"
# BURMA_OAKLAND_MAX_PAGE = 30
BURMA_OAKLAND_MAX_PAGE = 2470

BURMA_ALAMEDA_URL = 'burma-superstar-alameda-2'
BURMA_ALAMEDA_MAX_PAGE = 2000

# Bypass SSL that prevents me from opening up a URL via python.
def bypassSSL():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

# Export a string to a file
def export(filepath, contents):
    with open(filepath, 'w') as file:
        file.write(contents)
    print(f'Exported contents to {filepath}')

# Get review attributes to use in data analysis
def get_review_attributes(review_html):
    # CONSTANTS FOR REVIEW ATTRIBUTE DICT KEYS
    DATE = 'review_date'
    RATING = 'review_rating'
    COMMENT = 'review_comment'
    WORD_COUNT = 'review_word_count'
    CHAR_LENGTH = 'review_char_length'
    PHOTO_COUNT = 'review_photo_count'

    # Get all review attributes and store in dict
    review_attributes = {}
    try:
        # Get user id
        user_contents = review.find('div', {'class':'user-passport-info'})
        review_attributes[USER_ID_KEY] = user_contents.a.get('href').replace('/user_details?userid=','')

        # Get review header information
        review_attributes[DATE] = review.find('span', {'class':'css-e81eai'}).get_text()
        review_attributes[RATING] = review.find('div', {'class': 'i-stars__373c0___sZu0'}).get('aria-label')

        # Get photo count
        photo_html = review.find('span', {'class':'css-1x0u7iy'})
        review_attributes[PHOTO_COUNT] = photo_html.get_text() if photo_html else '0'

        # Get emoji counts
        review_attributes.update(get_review_emjoi_counts(review))

        # Get review comments attributes
        review_comments = review.find('p', {'class':COMMENT_HTML}).span.get_text()
        review_attributes[WORD_COUNT] = len([review_comments][0].split())
        review_attributes[CHAR_LENGTH] = len(review_comments)
        review_attributes[COMMENT] = review_comments

    except AttributeError:
        print("Attribute error in review html")

    return review_attributes
    

# Get review emoji attributes such as Useful, Funny and Cool
def get_review_emjoi_counts(review_html):
    emojis = []
    attribute_buttons = review_html.find_all('button', {'class':'button__373c0__pdh_X css-q7z7wg'})
    for button in attribute_buttons:
            try:
                attribute = [button.find('span', {'class': 'css-1ha1j8d'}).get_text()]
                attribute_clean = attribute[0].split()
                if len(attribute_clean) == 1:
                    attribute_clean.append('0')
                emojis.append(attribute_clean)
            except AttributeError:
                print("Attribute error in button")
    emojis_dict = {emojis[i][0]: emojis[i][1] for i in range(len(emojis))}
    return emojis_dict

# Find indices of a given string
def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]


print("\n**************************")
print("Start program")
print("**************************")
# TODO catch a HTTPError
bypassSSL()

main_url = YELP_BIZ_URL + BURMA_OAKLAND_URL
reviews = []
user_ids = []
url_string_errors = []
for page in range(0, BURMA_OAKLAND_MAX_PAGE, 10):
    soup = None
    url_string = main_url if page == 0 else f'{main_url}?start={page}'
    sleep(SLEEP_SEC)
    print(f'Sleeping for {SLEEP_SEC} & then access {url_string}')
    try:
        url = urllib.request.urlopen(url_string)
        soup = bs(url, 'html.parser')
        # output_file = DIRECTORY + "output.html"
        # export(output_file, soup.prettify())

        # Get all reviews on the given page
        REVIEW_HTML = "margin-b5__373c0__3ho0z"
        COMMENT_HTML = 'comment__373c0__Nsutg'
        review_htmls = soup.find_all('li', {'class':REVIEW_HTML})

        # Get the attributes for the reviews
        for review in review_htmls:
            review_attributes = get_review_attributes(review)
            reviews.append(review_attributes)
            user_ids.append(review_attributes[USER_ID_KEY])
            print(f'got all review attributes for {review_attributes[USER_ID_KEY]}')
    except:
        print(f'Htttp error for {url_string}')
        url_string_errors.append(url_string)
        
# TODO Export data in a csv
string_reviews = ''
string_user_ids = ''
for review in reviews:
    string_reviews = string_reviews + str(review) + '\n'

for id in user_ids:
    string_user_ids = string_user_ids + str(id) + '\n'

export(DIRECTORY + 'reviews_burma_oakland_output.txt', string_reviews)
export(DIRECTORY + 'user_ids_burma_oakland_output.txt', string_user_ids)
print("exported")
print(f'url string errors: {url_string_errors}')
print("**************************")
print("End program")
print("**************************\n")