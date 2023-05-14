import requests

from secret import API_URL

if not API_URL:
    API_URL = input("Enter API URL: ")


class API:
    """Class that enables communication with an Azure Function API.
    """

    def __init__(self, url:str):
        self.url = url

    def get_count(self) -> dict[int]:
        """Returns latest counts from the API.

        Returns:
            dict[int]: Latest counts of all classes.
        """
        response = requests.get(self.url)
        latest = response.json()[-1]
        return {
            'paper': latest['paper'],
            'container': latest['container'],
            'other': latest['other'],
        }

    def post_count(self, counts:dict[int]) -> dict:
        """Posts incremental sum of total class counts to the API.

        Args:
            counts (dict[int]): Counts of classes in the last time period.

        Returns:
            dict: Latest database entry.
        """
        prev_count = self.get_count()

        counts['paper'] += prev_count['paper']
        counts['container'] += prev_count['container']
        counts['other'] += prev_count['other']

        response = requests.post(self.url, json=counts)
        return response.json()


if __name__ == "__main__":
    """Used for testing purposes.
    """
    api = API(API_URL)
    print(api.get_count())
    print(api.post_count({'paper': 0, 'container': 0, 'other': 0}))
