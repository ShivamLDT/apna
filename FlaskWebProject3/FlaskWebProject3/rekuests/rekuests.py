import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Rekuest:
    def __init__(self, retries=3, backoff_factor=1, status_forcelist=None, timeout=(5, 500)):
        # Set default values if none are provided
        if status_forcelist is None:
            status_forcelist = [500, 502, 503, 504]
        
        # Store the timeout value
        self.timeout = timeout
        
        # Create a session
        self.session = requests.Session()

        # Configure the retry strategy
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["POST"]  # Apply retry logic to POST requests
        )

        # Mount the retry strategy to the session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def post(self, url, data=None, json=None, **kwargs):
        """
        Method to handle POST requests with retries and timeout.
        """
        # Set default timeout if not provided in kwargs
        kwargs.setdefault('timeout', self.timeout)
        
        # Make the POST request with the session
        try:
            response = self.session.post(url, data=data, json=json, **kwargs)
            return response
        except requests.exceptions.Timeout:
            print(f"Request to {url} timed out.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

# # Example Usage
# request_handler = Rekuest()

# # Call the post method
# response = request_handler.post('https://localhost:53335', data={'key': 'value'})

# if response:
#     print(response.status_code)
# else:
#     print("Request failed or timed out.")

