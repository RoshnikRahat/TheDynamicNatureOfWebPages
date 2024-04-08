# refrences: https://saturncloud.io/blog/how-to-extract-dictionary-values-from-a-pandas-dataframe/#understanding-pandas-dataframe

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import regex as re
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde

website_categories = {
    "https://finance.yahoo.com": "Economy/Finance",
    "https://m.economictimes.com": "Economy/Finance",
    "https://www.bloomberg.com": "Economy/Finance",
    "https://www.lemonde.fr": "News",
    "https://www.bbc.co.uk": "News",
    "https://www.cnn.com": "News",
    "https://stackoverflow.com": "Education",
    "https://www.typing.com": "Education",
    "https://www.dzexams.com": "Education",
    "https://www.healthline.com": "Health",
    "https://www.verywellhealth.com": "Health",
    "https://health.findanyanswer.net": "Health",
    "https://www.starhealth.in": "Health",
    "https://www.livescore.com": "Sports",
    "https://www.nikkansports.com": "Sports",
    "https://www.cricbuzz.com": "Sports",
    "https://www.goojara.to": "Entertainment",
    "https://aniwatchtv.to": "Entertainment",
    "https://www.netflix.com": "Entertainment",
    "https://www.amazon.com.tr": "Online Retail",
    "https://es.aliexpress.com": "Online Retail",
    "https://www.ebay.com": "Online Retail",
    "https://www.gov.uk": "Government",
    "https://www.turkiye.gov.tr": "Government",
    "https://www.gov.br": "Government",
    "https://pubmed.ncbi.nlm.nih.gov": "Government",
    "https://weather.com": "Weather",
    "https://www.theweathernetwork.com": "Weather",
    "https://weathernews.jp": "Weather",
    "https://m.timesofindia.com": "News",
    "https://www.doubtnut.com": "Education",
    "https://www.myntra.com": "Online Retail",
    "https://www.primevideo.com": "Entertainment",
    "https://www.tjk.org": "Sports",
    "https://www.diretta.it":"Sports",
    "https://www.paypal.com":"Economy/Finance"
}


# Reading Data and Assigning categories
df=pd.read_csv("2024-03-30cache_httpHeader.csv",quotechar='"')
df["category"]= [website_categories[x] for x in df['url']]
print(df.head())

# plotting cache by column

sns.countplot(data=df, x="category",hue="IsCacheInfoAvailable")
plt.show()
grouped_df = df.groupby(['category', 'IsCacheInfoAvailable']).size().reset_index(name='count')
# Plotting
fig = px.bar(grouped_df, x='category', y='count', color='IsCacheInfoAvailable', barmode='group')
fig.update_traces(marker_color=['green', 'red'])  # Change the colors to dark green and red

fig.update_layout(
    title="Count of IsCacheInfoAvailable by Category",
    title_x=0.5,
    title_font=dict(size=42),
    legend=dict(
        orientation='h',  # horizontal legend
        yanchor='top',
        y=1,
        xanchor='right',
        x=0.8,
        font=dict(size=42)  # increase legend text size
    ),
    xaxis=dict(
        titlefont=dict(size=42),  # increase x-axis label text size
        tickfont=dict(size=42)  # increase x-axis tick text size
    ),
    yaxis=dict(
        titlefont=dict(size=42), 
        tickfont=dict(size=42)  # increase y-axis tick text size
    )
)
fig.show()
#plt.show()
# print(df.columns)

# plotting cache where cache info exists and seeing if maxage exists and is greater than 1 

def extract_max_age(cache_info):
    match = re.search(r"max-age=(\d+)", cache_info)
    if match:
        return int(match.group(1))
    else:
        return None


df['max_age'] =df[df['IsCacheInfoAvailable']]['CacheInfo'].apply(extract_max_age)
print(df[df['IsCacheInfoAvailable']]['max_age'].describe())
print(df[df['IsCacheInfoAvailable']]['max_age'].value_counts())
print(df['max_age'].isnull().sum())
sns.kdeplot(data=df[df['IsCacheInfoAvailable']],x=df[df['IsCacheInfoAvailable']]['max_age'], cut=0)
#plt.show()

# Filtering the DataFrame based on the 'IsCacheInfoAvailable' column and dropping values above 1500
filtered_df = df[df['IsCacheInfoAvailable']]
filtered_df = filtered_df[filtered_df['max_age'] <= 1500]

# Creating the KDE plot using Plotly

fig = px.scatter(
    filtered_df, x="max_age",y='category', marginal_x="box",  # Maintain boxplot on x-axis
)

# Optionally adjust boxplot color
fig.update_layout(
    title="Max-Age Distribution between 0-1500 seconds across categories",
    title_x=0.5,
    title_font=dict(size=42),
    xaxis=dict(
        title="Max-Age",  # Set the new x-axis label
        title_font=dict(size=42),  # Adjust the font size of x-axis label
        tickfont=dict(size=42),  # Adjust the font size of x-axis tick labels
    ),
    yaxis=dict(
        title="Categoty",  # Set the new y-axis label
        title_font=dict(size=42),  # Adjust the font size of y-axis label
        tickfont=dict(size=42),  # Adjust the font size of y-axis tick labels
    ),
)

fig.update_traces(marker={'size': 30,'color':"blue"}) # Darker boxplot fill and lines

fig.show()
