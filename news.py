import requests

def search_keyword(keyword, date_published_from=None, date_published_to=None, domain=None, language=None):
    api_key = 'ebbd63f1bafa4347b339797845694480'
    url = 'https://newsapi.org/v2/everything'

    params = {
            'q': keyword,  # The keyword you want to search for
            'apiKey': api_key,   
            'sortBy': 'relevancy',  # Sort the results by relevancy
        }

    if date_published_from:
        params['from'] = date_published_from  # Format: 'yyyy-mm-dd'
    
    if date_published_to:
        params['to'] = date_published_to  # Format: 'yyyy-mm-dd'

    if language:
        params['language'] = language  

    if domain:
        params['domains'] = domain  
        
    try:
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Convert the response to JSON format
            news_data = response.json()
            return news_data['articles']  # Return a list of articles
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

articles = search_keyword('France Riot', '2023-06-28', '2023-07-10', None, 'en')

if articles:
    for article in articles:
        print(article['title'])
        print(article['description'])
        print(article['url'])
        print('-' * 50)