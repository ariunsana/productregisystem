from django.shortcuts import render
import requests

def fetch_data(query):
    url = 'http://127.0.0.1:8080/graphql/'
    try:
        # Use urlencode to add the query as a URL parameter
        params = {'query': query}
        response = requests.get(url, params=params)  # Use GET request

        # Check if the response status is 200 (OK)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return None  # Return None in case of failure
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
def branch(request):
    query = """
    query BranchListQuery {
      branches {
        branchName
        branchLocation
        img
        branchId
      }
    }
    """
    data = fetch_data(query)
    
    if data and 'data' in data and 'branches' in data['data']:
        branch_data = data['data']['branches']
    else:
        branch_data = []  # Default to an empty list if no data is available

    return render(request, 'branch.html', {'branches': branch_data})

def index(request):
    return render(request, 'index.html')

def signin(request):
    return render(request, 'signin.html')

def register(request):
    return render(request, 'register.html')

def products(request):
    return render(request, 'products.html')

def category(request):
    return render(request, 'category.html')

def seller(request):
    return render(request, 'seller.html')

def settings(request):
    return render(request, 'settings.html')

def report(request):
    return render(request, 'report.html')

def notifications(request):
    return render(request, 'notifications.html')
