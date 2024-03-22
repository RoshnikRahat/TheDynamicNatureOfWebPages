#ref: https://stackoverflow.com/questions/679218/the-best-way-to-inspect-http-response-headers-with-selenium
#ref: https://www.geeksforgeeks.org/http-headers-cache-control/
import pandas as pd
import requests
from datetime import datetime
def get_cache_headers(url):
  """
  Fetches the cache headers from a website and returns a dictionary.
  """

  response = requests.head(url)
  headers = response.headers
  cache_info = {}
  for key, value in headers.items():
    if key.lower().startswith("cache-control"):
      cache_info[key] = value
  return cache_info

def main():
  """
  Gets URL from argument, fetches cache headers and stores in pandas dataframe.
  """
  cache_df=pd.DataFrame(columns=['time','url','IsCacheInfoAvailable','CacheInfo'])
  with open('websites.txt',encoding='utf-8-sig') as f:
    urls = [x.rstrip() for x in f]
  print(urls)
  for url in urls:
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cache_info = get_cache_headers(url)
    print(cache_info)
    if cache_info:
        row_data = {
            'time':current_datetime,
            'url': url,
            'IsCacheInfoAvailable': True,
            'CacheInfo':cache_info   
        }
        # Append the dictionary as a new row to the DataFrame
        cache_df.loc[len(cache_df)] = row_data

    else:
        row_data = {
            'time':current_datetime,
            'url': url,
            'IsCacheInfoAvailable': False,
        }
        print("No Cache-Control headers found for", url)
        cache_df.loc[len(cache_df)] = row_data
  cache_df.to_csv(str(datetime.now().date())+"cache_httpHeader")


if __name__ == "__main__":
  main()