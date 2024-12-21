from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
import requests
from django.shortcuts import get_object_or_404

GRAPHQL_ENDPOINT = 'http://localhost:8080/graphql/'
# Function to send GraphQL requests

def fetch_mutation_data(mutation, variables):
    try:
        payload = {
            'query': mutation,
            'variables': variables
        }
        response = requests.post(GRAPHQL_ENDPOINT, json=payload) 

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
def fetch_data(query):
    try:
        # Use urlencode to add the query as a URL parameter
        params = {'query': query}
        response = requests.get(GRAPHQL_ENDPOINT, params=params)  # Use GET request

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

def branch_list(request):
    query = """
    query BranchListQuery {
      branches {
        branchId
        branchName
        branchLocation
        img
      }
    }
    """
    data = fetch_data(query)
    
    if data and 'data' in data and 'branches' in data['data']:
        branch_data = data['data']['branches']
    else:
        branch_data = []  # Default to empty list if no data

    return render(request, 'branch.html', {'branches': branch_data})


def create_branch(request):
    if request.method == "POST":
        branch_name = request.POST.get("branchName")
        branch_location = request.POST.get("branchLocation")
        img = request.FILES.get("img")  # Access the uploaded image file

        # If the image is provided, save it to the filesystem
        if img:
            img_path = default_storage.save('photos/branch/' + img.name, ContentFile(img.read()))
            img_url = default_storage.url(img_path)  # Get the URL of the image
        else:
            img_url = None  # If no image is uploaded, set to None

        slug = request.POST.get("slug")

        mutation = """
        mutation CreateBranch($branchName: String!, $img: String, $branchLocation: String) {
            createBranch(branchName: $branchName, img: $img, branchLocation: $branchLocation) {
              branch {
                branchId
                branchName
                branchLocation
                img
                slug
              }
            }
        }
        """
        variables = {
            "branchName": branch_name,
            "img": img_url,  # Pass the image file path
            "branchLocation": branch_location,
            "slug": slug
        }

        response_data = fetch_mutation_data(mutation, variables)

        if response_data is None:
            print("Error: No valid response from the server.")
            return render(request, 'create_branch.html', {'error': 'Failed to create branch'})

        if 'errors' in response_data:
            print(f"GraphQL errors: {response_data['errors']}")
            return render(request, 'create_branch.html', {'error': response_data['errors'][0]['message']})

        if 'data' in response_data and 'createBranch' in response_data['data']:
            created_branch = response_data['data']['createBranch']['branch']
            print(f"Created Branch: {created_branch}")
            return redirect('branch_list')

        else:
            print("Error: No branch data returned from GraphQL.")
            return render(request, 'create_branch.html', {'error': 'Failed to create branch'})

    return render(request, 'create_branch.html')

def update_branch(request, branch_id):
    if request.method == "POST":
        branch_name = request.POST.get("branch_name")
        slug = request.POST.get("slug")
        img = request.POST.get("img")
        branch_location = request.POST.get("branch_location")

        mutation = """
        mutation UpdateBranch($branchId: Int!, $branchName: String, $slug: String, $img: String, $branchLocation: String) {
          updateBranch(branchId: $branchId, branchName: $branchName, slug: $slug, img: $img, branchLocation: $branchLocation) {
            branch {
              branchId
              branchName
              branchLocation
              img
            }
          }
        }
        """
        variables = {
            "branchId": branch_id,
            "branchName": branch_name,
            "slug": slug,
            "img": img,
            "branchLocation": branch_location
        }
        fetch_mutation_data(mutation, variables)
        return redirect('branch_list')  # Redirect to the branch list after updating

    # Fetch the current branch data to pre-fill the form
    query = """
    query GetBranch($branchId: Int!) {
      branch(branchId: $branchId) {
        branchId
        branchName
        branchLocation
        img
      }
    }
    """
    variables = {"branchId": branch_id}
    data = fetch_mutation_data(query, variables)
    branch_data = data.get('data', {}).get('branch', {})
    
    return render(request, 'update_branch.html', {'branch': branch_data})  # Render a form for updating a branch

def delete_branch(request, branch_id):
    if request.method == "POST":
        mutation = """
        mutation DeleteBranch($branchId: Int!) {
          deleteBranch(branchId: $branchId) {
            success
          }
        }
        """
        variables = {"branchId": branch_id}
        fetch_mutation_data(mutation, variables)
        return redirect('branch_list')  # Redirect to the branch list after deletion

    return render(request, 'delete_branch.html', {'branch_id': branch_id})  # Render a confirmation page for deletion

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
