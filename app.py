#imports for website dev/plotting
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px

from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

#imports for data + manipulation
import pandas as pd
import numpy as np
import imdb
from bs4 import BeautifulSoup
import requests
import re

#other imports
import os

####

rachel_df = pd.read_csv('https://raw.githubusercontent.com/ck-duong/dsc106/master/hw4/rachel.csv', index_col = 0)

countries = rachel_df['countries']
countries = countries.str.strip('[]').str.split(',\s+').apply(lambda x: pd.Series(x).value_counts()).sum()
countries = countries.reset_index()
countries['index'] = countries['index'].str.replace("'", "")
countries = countries.rename({'index': 'Country', 0: 'Movie Count'}, axis = 1)

chlor_map = px.choropleth(countries, locations =  'Country', locationmode = 'country names', color = 'Movie Count',
                         title = 'Going All the Way (Around the World)')

dropped = rachel_df.dropna(subset = ['domestic', 'international'])\
[['original title', 'year', 'domestic', 'international', 'total']]

grouped = dropped.groupby('year')[['domestic', 'international', 'total']].sum().reset_index().sort_values('total')

labels = grouped['year'].tolist()
parents = ['Rachel Weisz Movies' for x in labels]
values = grouped['total'].tolist()

labels.append('Rachel Weisz Movies')
parents.append('')
values.append(grouped['total'].sum())

def divide_gross(row):
    total = row['total']
    title = row['original title']
    parent = row['year']
    
    labels.append(title)
    parents.append(parent)
    values.append(total)

dropped.apply(divide_gross, axis = 1)

tree = go.Figure(go.Treemap(
    labels = labels,
    parents = parents,
    values = values,
    branchvalues = 'total',
    textinfo = "label+value+percent parent",
),
                go.Layout(title = 'Rachel the Great and Powerful'))

text = rachel_df['plot'].str.cat(sep=' ').lower()
text = text.replace(':', '').replace('-', '').replace(',','').replace('.', '').strip(' ').replace('"', '').replace("'", '')

stopwords = set(STOPWORDS)
stopwords.update(["Anonymous", 'IMDb', ' '])

words = pd.Series(text.split(' ')).value_counts()
words = words.loc[~words.index.isin(stopwords)]
words = words[words.index != '']
words = words.to_frame('count').reset_index().rename({'index': 'word'}, axis = 1)
words['rank'] = words.index + 1
words = words[['rank', 'word', 'count']]

tab = go.Figure([go.Table(
    header=dict(values=list(words.columns),
                align='left'),
    cells=dict(values=[words['rank'], words['word'], words['count']],
               align='left'))
], go.Layout(title = 'The Favourites'))

####

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children = [
    html.H1(children = "The Weisz Legacy: Rachel Weisz's Legendary Filmography",
           style={
            'textAlign': 'center'
        }),
    html.Div(html.Img(src = 'https://media.giphy.com/media/5bs4q5vpOSl9ViI42r/giphy.gif',
                style={
                'height': '25%',
                'width': '25%'
            }), style={'textAlign': 'center'}),
    html.P("Rachel Weisz is an established actress who has received several accolades, including an Oscar and British Academy Film Award. Weisz came into fame in the early 2000s with her breakout role in the popular film 'The Mummy'. Since then, Weisz has acted in a varity of films across the range of genres and has recently found more academy success in her role as Sarah Churchill in the black comedy period piece, 'The Favourite'. "),
    html.Br(),
    html.P('Easter Egg: All headings are puns based off of movies Weisz has starred in!'),
    html.Div(children = [
        html.H3('Going All the Way (Around the World)'),
        html.H5("Choropleth Map: Where Rachel Weisz Movies Are Produced"),
        html.P('This choropleth map shows the countries in which Rachel Weisz movies are produced in. Some movies may have multiple produciton locations, such as Disobidience which was produced in the United States, United Kingdom, and Ireland. In this case, all locations are counted seperately (meaning that Disobidience contributed to the count for the US, UK and Ireland). To interact with this graph, you can zoom in, scroll, and hover to see the values of each country and further examine the map. Originally, I was going to animate the graph by year, but since Weisz only makes a few movies a year, I felt that a total production country count map was more effective and interesting.'),
        html.Br(),
        html.P("Looking at the map, we can see that a majority of Weisz's movies are produced in the US and the UK, both of which are very dominant countries in the film industry. However, we also see that Weisz has worked in films produced in countries such as Brazil, Greece, and Kenya. She has not only a strong working history in the US and the UK, but also in France and Germany. This differs from many popular Hollywood actors who have mainly worked in American and British films like Robert Downey Jr. who has almost exclusively worked with American productions."),
        dcc.Graph(figure = chlor_map)
    ]),
    html.Div(children = [
        html.H3('Rachel the Great and Powerful'),
        html.H5('Treemap: Total (Domestic and International) Gross of Rachel Weisz Movies'),
        html.P("This treemap visualizes the overall gross of movies that Rachel Weisz has been casted in. The data is seperated by year, meaning that users can view how much each year contributed to the overall Weisz Movie gross. For each year, both the domestic and international gross of movies were counted. If a movie's gross was not listed on boxofficemojo (whether because it has not been released, did not receive a commercial release, etc.), it was excluded from the visualization. Each nested box within the year boxes represents a movie and displays its total gross and its gross as a percentage of the total gross for the year. To interact with this graph, you can click on the nodes (rectanges) and drill into the year, movies, etc."),
        html.Br(),
        html.P("Looking at the treemap, we can see that Weisz found the most commercial success (if we're just using overall movie gross as a measure of success) in the early 2000s as well as 2013. She was most successful in 2001, 2013, and 1999. In both 2001 and 1999, her commercial success can be attributed to The Mummy film series, with The Mummy Returns making up 82% of Weisz's 2001 gross at $433,013,274 and The Mummy making up 98% of Weisz's 1999 gross at $415,933,406. From this chart, we also can see that when Weisz does multiple movies a year, such as in 2001, 2005, and 2009, one of her movies greatly outperforms the other. In recent years, Weisz has not reached the same commercial success as she had in the early 2000s, but still has received favorable reviews for her acting, most notably in The Favourite and Disobidience which received Oscar and British Independent Film Awards nominations among others."),
        dcc.Graph(figure = tree)
    ]),
    html.Div(children = [
        html.H3('The Favourites'),
        html.H5('Wordcloud and Interative Table: Commonly Used Words in Plot Summaries of Rachel Weisz Movies'),
        html.P('This wordcloud represents the words commonly found in the plot summaries of movies Rachel Weisz is casted in. The plot data attribute is not present in all movies, and ones without it were dropped during the making of this tagcloud. To clean the text data, all text was converted to lowercase and punctuation was removed. The wordcloud itself is static.'),
        html.Br(),
        html.P("From the wordcloud, we can see that 'young' and 'friend' are both popular words that occur in plot summaries of movies that Weisz is casted in. Though this may imply that Weisz typically stars in feel-good or family movies, there is a good variety of words of various connotations and moods. Other prominent words in her cloud include murder, help, love, world, and journey, which demonstrates Weisz's acting capabilities and ability to work in many genres ranging from romance to drama to thriller."),
        html.Div(html.Img(src = 'https://github.com/ck-duong/dsc106/blob/master/hw4/wordcloud.png?raw=true',
                style={
                'height': '75%',
                'width': '75%'
            }), style={'textAlign': 'center'})
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)