import streamlit as st
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from wordcloud import WordCloud
from collections import Counter


# http://amueller.github.io/word_cloud/auto_examples/colored_by_group.html
class SimpleGroupedColorFunc(object):
    """Create a color function object which assigns EXACT colors
       to certain words based on the color to words mapping

       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.word_to_color = {word: color
                              for (color, words) in color_to_words.items()
                              for word in words}

        self.default_color = default_color

    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word, self.default_color)


def main():
    decklists_url = "https://magic.wizards.com/en/content/deck-lists-magic-online-products-game-info"
    st.header('MTGO Decklists - Wordcloud Generator')
    st.write("Insert the URL containing the decklists.")
    st.write(f"You can find them here: {decklists_url}")

    # Working example to start the app.
    decklists_data = requests.get(decklists_url)
    decklists_soup = BeautifulSoup(decklists_data.content, 'html.parser')

    base_url = 'https://magic.wizards.com'
    modern_url = decklists_soup.select_one("a[href*=modern-challenge]")
    if not modern_url:
        modern_url = decklists_soup.select_one("a[href*=modern-preliminary]")

    default_url = urljoin(base_url, modern_url.get('href'))
    # default_url = 'https://magic.wizards.com/en/articles/archive/mtgo-standings/modern-challenge-2020-08-16'
    # Input box
    url = st.text_input('URL: ', default_url)
    # Preventing some malicious use.
    valid_url = url.startswith('https://magic.wizards.com/')
    
    if not valid_url:
        st.write('Insert a valid URL from the official mtgo-standings.')
    if valid_url:
        try:
            fig = build_wordcloud(url)
            # Without these options the figure has an annoying white border.
            st.pyplot(fig, transparent=True, bbox_inches='tight', pad_inches=0)
        except ValueError:
            st.write('The URL does not contain decklists or they changed the layout.')


def build_wordcloud(url):
    """
    Scrape MTGO decklists from the official MTGO Archives
    and generate a matplotlib plot with a wordcloud.

    Parameters
    ----------
    url : str
        A valid URL from the Wizards of the Coast website
        containing decklists.
    """

    site_data = requests.get(url)
    soup = BeautifulSoup(site_data.content, 'html.parser')

    containers = soup.find_all('div', attrs={'class': 'sorted-by-overview-container'})

    # Each decklist is contained in one of those divs.
    decklists = [container.find_all('span', attrs={'class': 'row'}) for container in containers]

    card_list = list()
    for decklist in decklists:
        for card in decklist:
            card_name = card.find('span', attrs={'class': 'card-name'}).get_text()
            copies = int(card.find('span', attrs={'class': 'card-count'}).get_text())
            card_list.extend(copies * [card_name])

    # Create a frequency dict from the list.
    card_counter = Counter(card_list)

    # Pick which cards are which colors.
    colors = ['white', 'blue', 'black', 'red', 'green', 'multi', 'colorless']
    color_to_words = dict()
    for color in colors:
        cards = list()
        for decklist in soup.find_all('div', attrs={'class': f'sorted-by-{color}'}):
            for card in decklist.find_all('span', attrs={'class': 'card-name'}):
                cards.append(card.get_text())
        color_to_words[color] = cards

    # Assign a specific RGB color for each of the MTG colors.
    # I took these from the original mana symbols.
    color_to_words['#fcfcc1'] = color_to_words.pop('white')
    color_to_words['#67c1f5'] = color_to_words.pop('blue')
    color_to_words['#846484'] = color_to_words.pop('black')
    color_to_words['#f85555'] = color_to_words.pop('red')
    color_to_words['#26b569'] = color_to_words.pop('green')
    color_to_words['#cfaa4a'] = color_to_words.pop('multi')
    color_to_words['#6b5441'] = color_to_words.pop('colorless')

    # Create a set containing the lands to filter them out.
    lands_list = set()
    for decklist in soup.find_all('div', attrs={'class': 'sorted-by-land'}):
        for card in decklist.find_all('span', attrs={'class': 'card-name'}):
            lands_list.add(card.get_text())

    for card in lands_list:
        del card_counter[card]


    cloud = WordCloud(
        background_color='black',
        width=400,
        height=250,
        scale=5,
        ).generate_from_frequencies(card_counter)

    # Apply the chosen colors to the wordcloud.
    grouped_color_func = SimpleGroupedColorFunc(color_to_words, default_color='black')
    cloud.recolor(color_func=grouped_color_func)

    # Plot the cloud to matplotlib.
    # Normally, you'd call plt.show() to show the plot.
    fig = plt.figure(figsize = (16,9))
    plt.imshow(cloud)
    plt.axis("off")
    return fig


if __name__ == '__main__':
    main()

