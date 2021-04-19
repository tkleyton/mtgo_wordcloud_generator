# MTGO Decklists - Wordcloud Generator

Magic: The Gathering Online frequently publishes decklists that performed well in their tournaments.  
I figured it would be convenient to have a quicker way to assess the cards you should keep in mind when playing other than skimming through all the decklists published.  
A WordCloud seemed like a good visualization of those results.

This [Streamlit](https://www.streamlit.io/) app is a quick prototype so that anyone can generate their own WordCloud.  
This app is hosted on Heroku from this repo: <https://mtgo-wordcloud.herokuapp.com/>  
Just plug the URL and you're good to go.

## Running locally

This runs on Python3. Assuming you have a running Python3 in your machine:

    pip install -r requirements.txt
    streamlit run app.py

To stop the application, press CTRL+C.
