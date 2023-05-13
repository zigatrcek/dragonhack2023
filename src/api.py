import requests
from secret import API_URL

if not API_URL:
    API_URL = input("Enter API URL: ")

class API:
    """Class that enables communication with an Azure Function API.
    """
    def __init__(self, url):
        self.url = url

    def get_count(self):
        response = requests.get(self.url)
        latest = response.json()[-1]
        return {
            'paper': latest['paper'],
            'container': latest['container'],
            'other': latest['other']
        }

    def post_count(self, count):
        prev_count = self.get_count()

        count['paper'] += prev_count['paper']
        count['container'] += prev_count['container']
        count['other'] += prev_count['other']

        response = requests.post(self.url, json=count)
        return response.json()

if __name__ == "__main__":
    api = API(API_URL)
    print(api.get_count())
    print(api.post_count({'paper': 0, 'container': 0, 'other': 0}))
