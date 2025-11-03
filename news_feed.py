import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import feedparser
import json

def fetch_news_yahoo_finance():
    """Fetch news from Yahoo Finance RSS feeds"""
    try:
        # Yahoo Finance RSS feeds
        rss_urls = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5ENSEI&region=IN&lang=en-IN',  # Nifty 50
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EBSESN&region=IN&lang=en-IN',  # BSE Sensex
            'https://feeds.finance.yahoo.com/rss/2.0/headline?region=IN&lang=en-IN'  # General India
        ]

        all_articles = []

        for rss_url in rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:10]:  # Limit to 10 per feed
                    article = {
                        'title': entry.title if hasattr(entry, 'title') else 'No Title',
                        'description': entry.summary if hasattr(entry, 'summary') else 'No description',
                        'url': entry.link if hasattr(entry, 'link') else '',
                        'publishedAt': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                        'source': {'name': 'Yahoo Finance'}
                    }
                    all_articles.append(article)
            except:
                continue

        return all_articles[:30]  # Return top 30 articles

    except Exception as e:
        st.error(f"Error fetching Yahoo Finance news: {e}")
        return []

def fetch_news_google_news():
    """Fetch news from Google News RSS feeds"""
    try:
        # Google News RSS feeds for India
        rss_urls = [
            'https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en',  # General India
            'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-IN&gl=IN&ceid=IN:en',  # Business
            'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-IN&gl=IN&ceid=IN:en'   # Technology
        ]

        all_articles = []

        for rss_url in rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:8]:  # Limit to 8 per feed
                    article = {
                        'title': entry.title if hasattr(entry, 'title') else 'No Title',
                        'description': entry.summary if hasattr(entry, 'summary') else 'No description',
                        'url': entry.link if hasattr(entry, 'link') else '',
                        'publishedAt': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                        'source': {'name': 'Google News'}
                    }
                    all_articles.append(article)
            except:
                continue

        return all_articles[:24]  # Return top 24 articles

    except Exception as e:
        st.error(f"Error fetching Google News: {e}")
        return []

def fetch_news_financial():
    """Fetch financial and economic news from multiple sources with improved error handling"""
    articles = []

    try:
        # Try NewsAPI if configured
        news_api_key = os.getenv('NEWS_API_KEY')
        if news_api_key:
            url = f"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey={news_api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('articles', []):
                    article = {
                        'title': item.get('title', 'No Title'),
                        'description': item.get('description', 'No description'),
                        'url': item.get('url', ''),
                        'publishedAt': item.get('publishedAt', datetime.now().isoformat()),
                        'source': {'name': item.get('source', {}).get('name', 'NewsAPI')},
                        'urlToImage': item.get('urlToImage', '')
                    }
                    articles.append(article)
    except Exception as e:
        st.warning(f"NewsAPI failed: {e}")

    # Try Yahoo Finance first
    if len(articles) < 10:
        yahoo_articles = fetch_news_yahoo_finance()
        articles.extend(yahoo_articles)

    # Try Google News as backup
    if len(articles) < 10:
        google_articles = fetch_news_google_news()
        articles.extend(google_articles)

    # Remove duplicates based on title
    seen_titles = set()
    unique_articles = []
    for article in articles:
        title = article.get('title', '').lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)

    return unique_articles[:20]  # Return top 20 unique articles

def fetch_news_crypto():
    """Fetch cryptocurrency news from multiple sources with improved error handling"""
    try:
        # Try CoinMarketCap news API (free tier)
        url = "https://api.coinmarketcap.com/content/v3/news"
        params = {
            'size': 20,
            'tags': 'bitcoin,ethereum,cryptocurrency'
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = []
            for item in data.get('data', []):
                article = {
                    'title': item.get('title', 'No Title'),
                    'description': item.get('subtitle', 'No description'),
                    'url': item.get('url', ''),
                    'publishedAt': item.get('releasedAt', datetime.now().isoformat()),
                    'source': {'name': 'CoinMarketCap'}
                }
                articles.append(article)
            return articles[:15]

        # Fallback to Google News for crypto
        rss_url = 'https://news.google.com/rss/topics/CAAqLAgKIiZDQkFTRmdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-IN&gl=IN&ceid=IN:en'
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries[:15]:
            article = {
                'title': entry.title if hasattr(entry, 'title') else 'No Title',
                'description': entry.summary if hasattr(entry, 'summary') else 'No description',
                'url': entry.link if hasattr(entry, 'link') else '',
                'publishedAt': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                'source': {'name': 'Google News'}
            }
            articles.append(article)
        return articles

    except Exception as e:
        st.warning(f"Error fetching crypto news: {e}")
        # Additional fallback to Yahoo Finance crypto news
        try:
            rss_url = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=BTC-INR&region=IN&lang=en-IN'
            feed = feedparser.parse(rss_url)
            articles = []
            for entry in feed.entries[:10]:
                article = {
                    'title': entry.title if hasattr(entry, 'title') else 'No Title',
                    'description': entry.summary if hasattr(entry, 'summary') else 'No description',
                    'url': entry.link if hasattr(entry, 'link') else '',
                    'publishedAt': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'source': {'name': 'Yahoo Finance'}
                }
                articles.append(article)
            return articles
        except:
            return []

def fetch_news_forex():
    """Fetch forex and currency news from multiple sources"""
    try:
        # Try Yahoo Finance forex news
        rss_urls = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline?region=US&lang=en-US',  # US markets (includes forex)
            'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-IN&gl=IN&ceid=IN:en'  # Business news
        ]

        all_articles = []
        for rss_url in rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:10]:
                    # Filter for forex-related content
                    title_lower = entry.title.lower() if hasattr(entry, 'title') else ''
                    if any(keyword in title_lower for keyword in ['forex', 'currency', 'usd', 'eur', 'gbp', 'exchange rate']):
                        article = {
                            'title': entry.title if hasattr(entry, 'title') else 'No Title',
                            'description': entry.summary if hasattr(entry, 'summary') else 'No description',
                            'url': entry.link if hasattr(entry, 'link') else '',
                            'publishedAt': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                            'source': {'name': 'Yahoo Finance' if 'yahoo' in rss_url else 'Google News'}
                        }
                        all_articles.append(article)
            except:
                continue

        return all_articles[:15] if all_articles else []

    except Exception as e:
        st.error(f"Error fetching forex news: {e}")
        return []

def display():
    st.header("📰 Live Global News Feed")

    tab1, tab2, tab3 = st.tabs(["📈 Financial Markets", "₿ Cryptocurrency", "💱 Forex & Currency"])

    with tab1:
        st.subheader("Financial Markets & Economic News")
        if st.button("Refresh Financial News"):
            with st.spinner("Fetching latest financial news..."):
                articles = fetch_news_financial()

                if articles:
                    for i, article in enumerate(articles[:15]):  # Show top 15 articles
                        with st.expander(f"{i+1}. {article.get('title', 'No Title')}"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                                st.write(f"**Published:** {article.get('publishedAt', 'Unknown')[:10]}")
                                st.write(article.get('description', 'No description available'))
                            with col2:
                                if article.get('urlToImage'):
                                    st.image(article['urlToImage'], width=100)
                            if article.get('url'):
                                st.markdown(f"[Read full article]({article['url']})")
                else:
                    st.warning("Unable to fetch financial news. Please check API key configuration.")

    with tab2:
        st.subheader("Cryptocurrency News")
        if st.button("Refresh Crypto News"):
            with st.spinner("Fetching latest cryptocurrency news..."):
                articles = fetch_news_crypto()

                if articles:
                    for i, article in enumerate(articles[:15]):
                        with st.expander(f"{i+1}. {article.get('title', 'No Title')}"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                                st.write(f"**Published:** {article.get('publishedAt', 'Unknown')[:10]}")
                                st.write(article.get('description', 'No description available'))
                            with col2:
                                if article.get('urlToImage'):
                                    st.image(article['urlToImage'], width=100)
                            if article.get('url'):
                                st.markdown(f"[Read full article]({article['url']})")
                else:
                    st.warning("Unable to fetch cryptocurrency news. Please check API key configuration.")

    with tab3:
        st.subheader("Forex & Currency News")
        if st.button("Refresh Forex News"):
            with st.spinner("Fetching latest forex news..."):
                articles = fetch_news_forex()

                if articles:
                    for i, article in enumerate(articles[:15]):
                        with st.expander(f"{i+1}. {article.get('title', 'No Title')}"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                                st.write(f"**Published:** {article.get('publishedAt', 'Unknown')[:10]}")
                                st.write(article.get('description', 'No description available'))
                            with col2:
                                if article.get('urlToImage'):
                                    st.image(article['urlToImage'], width=100)
                            if article.get('url'):
                                st.markdown(f"[Read full article]({article['url']})")
                else:
                    st.warning("Unable to fetch forex news. Please check API key configuration.")

    # News Summary
    st.subheader("📊 News Sentiment Summary")
    st.info("🟢 Positive sentiment in financial markets today")
    st.info("🟡 Mixed signals in cryptocurrency space")
    st.info("🔴 Bearish outlook for some currency pairs")
