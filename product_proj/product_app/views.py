from django.core.files.storage import default_storage
import base64
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
    
def fetch_branch_by_id(branch_id):
    """
    Fetch branch details by branch_id using a GraphQL query.
    """
    query = """
    query FetchBranchById($branchId: Int!) {
        branches(branchId: $branchId) {
            branchId
            branchName
            slug
            img
            branchLocation
        }
    }
    """
    variables = {"branchId": branch_id}
    response = requests.post(
        GRAPHQL_ENDPOINT,
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        # If `branches` is a list, return the first item or handle appropriately
        branches = data.get("data", {}).get("branches", [])
        return branches[0] if branches else None
    else:
        raise Exception(f"Failed to fetch branch. Status code: {response.status_code}, Response: {response.text}")


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
        print(branch_data)  # Debugging line to check the structure
    else:
        branch_data = []  # Default to empty list if no data

    return render(request, 'branch/branch.html', {'branches': branch_data})

def create_branch(request):
    if request.method == "POST":
        branch_name = request.POST.get("branchName")
        branch_location = request.POST.get("branchLocation")
        img = request.FILES.get("img")

        # Convert image to base64 if provided
        base64_img = None
        if img:
            file_content = img.read()
            base64_img = base64.b64encode(file_content).decode('utf-8')

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
            "img": base64_img,  # Send base64 encoded image
            "branchLocation": branch_location,
        }

        response_data = fetch_mutation_data(mutation, variables)

        if response_data is None:
            return render(request, 'create_branch.html', {'error': 'Failed to create branch'})

        if 'errors' in response_data:
            return render(request, 'create_branch.html', {'error': response_data['errors'][0]['message']})

        if 'data' in response_data and 'createBranch' in response_data['data']:
            return redirect('branch_list')
        else:
            return render(request, 'create_branch.html', {'error': 'Failed to create branch'})

    return render(request, 'branch/create_branch.html')


def update_branch(request, branch_id):
    # Fetch the branch data to prepopulate the form
    branch = fetch_branch_by_id(branch_id)
    
    if request.method == "POST":
        branch_name = request.POST.get("branchName")
        branch_location = request.POST.get("branchLocation")
        img = request.FILES.get("img")  # Access the uploaded image file

        # Convert the image file to a Base64-encoded string if provided
        base64_img = None
        if img:
            file_content = img.read()  # Read the file content
            base64_img = base64.b64encode(file_content).decode('utf-8')  # Encode to Base64

        # Prepare the GraphQL mutation and variables
        mutation = """
        mutation UpdateBranch($branchId: Int!, $branchName: String, $img: String, $branchLocation: String) {
            updateBranch(branchId: $branchId, branchName: $branchName, img: $img, branchLocation: $branchLocation) {
                branch {
                    branchId
                    branchName
                    slug
                    img
                    branchLocation
                }
            }
        }
        """
        variables = {
            "branchId": branch_id,
            "branchName": branch_name,
            "img": base64_img,  # Include the Base64-encoded image
            "branchLocation": branch_location,
        }

        # Fetch mutation response
        response_data = fetch_mutation_data(mutation, variables)

        if response_data is None:
            print("Error: No valid response from the server.")
            return render(request, 'update_branch.html', {'error': 'Failed to update branch'})

        if 'errors' in response_data:
            print(f"GraphQL errors: {response_data['errors']}")
            return render(request, 'update_branch.html', {'error': response_data['errors'][0]['message']})

        if 'data' in response_data and 'updateBranch' in response_data['data']:
            updated_branch = response_data['data']['updateBranch']['branch']
            print(f"Updated Branch: {updated_branch}")
            return redirect('branch_list')

        else:
            print("Error: No branch data returned from GraphQL.")
            return render(request, 'update_branch.html', {'error': 'Failed to update branch'})

    return render(request, 'branch/update_branch.html', {'branch': branch})


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

    return render(request, 'branch/delete_branch.html', {'branch_id': branch_id})  # Render a confirmation page for deletion

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
