from bs4 import BeautifulSoup as bs    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from flashtext import KeywordProcessor # https://flashtext.readthedocs.io/en/latest/
import urllib.request
import ssl

# CONSTANTS
DIRECTORY = "/Users/E1T5/Desktop/Personal/"

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

# Find indices of a given string
def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

# Get unique list of user ids from file input
def get_user_id_urls(filepath):
    USER_URL_STRING = 'https://www.yelp.com/user_details?userid='

    ids = {}
    with open(filepath) as f:
        ids = set([f'{USER_URL_STRING}{line.strip()}' for line in f.readlines()])
    return ids

# Clean dictionary keys
def clean_dict_keys(dict):
    clean_dict = {}

    # Get a keyword replacer
    keyword_processor = KeywordProcessor() #unclean, clean
    keyword_processor.add_non_word_boundary('_')
    keyword_processor.add_non_word_boundary('.')
    keyword_processor.add_non_word_boundary("'")
    keyword_dict = {
        'review': 'reviews',
        'camera': 'photos',
        'compliment': 'thank_you', 
        'pencil': 'good_writer', 
        'flame': 'hot_stuff',
        'file': 'note', 
        'stat_light_bulb': 'stat_tips',
        "When I'm Not Yelping": 'When not yelping I',
        "Don't Tell Anyone Else But...": "Dont tell anybody that"
    }
    for key, value in keyword_dict.items():
        keyword_processor.add_keyword(key, value)
    
    for key, value in dict.items():
        clean_dict[keyword_processor.replace_keywords(key)] = value

    return clean_dict

# Get header level stats
def get_header_info(html):
    header_html = html.find('div', {'class':'user-profile_info'})
    user_attributes['name'] = header_html.h1.get_text().strip()
    li_html_items = header_html.find_all('li')
    labels = [info.use.get('xlink:href').strip('#24x24_') for info in li_html_items]
    values = [info.strong.get_text().strip() for info in li_html_items]
    header_dict = {labels[i] : values[i] for i in range(len(labels))}
    return header_dict

# Get ratings attributes
def get_ratings_attributes(html):
    rating_distribution = html.find('table', {'class':'histogram'})
    rating_labels_html = rating_distribution.find_all('th', {'class':'histogram_label'})
    rating_counts_html = rating_distribution.find_all('td', {'class':'histogram_count'})
    ratings_dict = {rating_labels_html[i].get_text().strip() : rating_counts_html[i].get_text() for i in range(len(rating_labels_html)) }
    print("** Extracted Ratings Distribution data")
    return ratings_dict

# Get specific stats
def get_specific_stats(html):
    user_stat_dict = {}
    y_sections = user_html.find_all('div', {'class':'ysection'})
    for section in y_sections:
        section_header = section.h4.get_text().strip() if section.h4 else ''
        li_html_items = section.find_all('li')

        if section_header == 'Review Votes':
            vote_types = [type.use.get('xlink:href').replace('_outline','')[7:] for type in li_html_items]
            counts = [vote.strong.get_text().strip() for vote in li_html_items]
            votes_dict = {f'vote_{vote_types[i]}': counts[i] for i in range(len(counts))}
            user_stat_dict.update(votes_dict)
            print("** Extracted Review Votes data")

        elif section_header == 'Stats':
            stats = [stat.use.get('xlink:href').strip('#18x18_') for stat in li_html_items]
            counts = [stat.strong.get_text().strip() for stat in li_html_items]
            stats_dict = {f'stat_{stats[i]}': counts[i] for i in range(len(stats))}
            user_stat_dict.update(stats_dict)
            print("** Extracted Stats data")

        elif 'Compliment' in section_header:
            icons = [f'{icon.use.get("xlink:href").replace("_","")[6:]}' for icon in li_html_items]
            counts = [icon.small.get_text().strip() for icon in li_html_items]
            compliments_dict = {f'badge_{icons[i]}' : counts[i] for i in range(len(icons))}
            user_stat_dict.update(compliments_dict)
            print("** Extracted Compliments data")

        elif section_header == 'Location':
            labels = [info.h4.get_text().strip() for info in li_html_items]
            values = [info.p.get_text().strip() for info in li_html_items]
            info_dict = {labels[i] : values[i] for i in range(len(labels))}
            user_stat_dict.update(info_dict)
            print("** Extracted Information data")

    return user_stat_dict

print("\n**************************")
print("Start program")
print("**************************")
bypassSSL()

user_id_url_strings = get_user_id_urls(DIRECTORY + 'users.txt')

for url_string in user_id_url_strings:
    # Get HTML of page
    url = urllib.request.urlopen(url_string)
    soup = bs(url, 'html.parser')
    # output_file = DIRECTORY + "user-dora-output.html"
    # export(output_file, soup.prettify())

    # Get the User HTML
    USER_HTML = 'main-content-wrap'
    COMMENT_HTML = 'comment__373c0__Nsutg'
    user_html = soup.find('div', {'class':USER_HTML})
    
    # Extract all user attributes
    user_attributes = {}
    user_attributes.update(get_header_info(user_html))
    user_attributes.update(get_ratings_attributes(user_html))
    user_attributes.update(get_specific_stats(user_html))

    # Clean up the attribute labels
    user_attributes_clean = clean_dict_keys(user_attributes)
    print(user_attributes_clean)

    # TODO Export data in a csv


print("**************************")
print("End program")
print("**************************\n")