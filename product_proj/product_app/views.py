import base64
from django.shortcuts import render, redirect
import requests

GRAPHQL_ENDPOINT = "http://localhost:8080/graphql/"
# Function to send GraphQL requests

def fetch_graphql_data(query_or_mutation, variables=None, method="POST"):
    try:
        payload = {"query": query_or_mutation}
        if variables:
            payload["variables"] = variables
        
        if method == "POST":
            response = requests.post(GRAPHQL_ENDPOINT, json=payload)
        elif method == "GET":
            params = {"query": query_or_mutation}
            response = requests.get(GRAPHQL_ENDPOINT, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
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
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        # If `branches` is a list, return the first item or handle appropriately
        branches = data.get("data", {}).get("branches", [])
        return branches[0] if branches else None
    else:
        raise Exception(
            f"Failed to fetch branch. Status code: {response.status_code}, Response: {response.text}"
        )

def fetch_branches():
    query = """
    query {
        branches {
            branchId
            branchName
        }
    }
    """
    
    response = requests.post(
        GRAPHQL_ENDPOINT,  # replace with your GraphQL API endpoint
        json={'query': query}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("branches", [])
    else:
        return []
    
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
    data = fetch_graphql_data(query)

    if data and "data" in data and "branches" in data["data"]:
        branch_data = data["data"]["branches"]
        print(branch_data)  # Debugging line to check the structure
    else:
        branch_data = []  # Default to empty list if no data

    return render(request, "branch/branch.html", {"branches": branch_data})

def create_branch(request):
    if request.method == "POST":
        branch_name = request.POST.get("branchName")
        branch_location = request.POST.get("branchLocation")
        img = request.FILES.get("img")

        # Convert image to base64 if provided
        base64_img = None
        if img:
            file_content = img.read()
            base64_img = base64.b64encode(file_content).decode("utf-8")

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

        response_data = fetch_graphql_data(mutation, variables)

        if response_data is None:
            return render(
                request, "create_branch.html", {"error": "Failed to create branch"}
            )

        if "errors" in response_data:
            return render(
                request,
                "create_branch.html",
                {"error": response_data["errors"][0]["message"]},
            )

        if "data" in response_data and "createBranch" in response_data["data"]:
            return redirect("branch_list")
        else:
            return render(
                request, "create_branch.html", {"error": "Failed to create branch"}
            )

    return render(request, "branch/create_branch.html")

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
            base64_img = base64.b64encode(file_content).decode(
                "utf-8"
            )  # Encode to Base64

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
        response_data = fetch_graphql_data(mutation, variables)

        if response_data is None:
            print("Error: No valid response from the server.")
            return render(
                request, "update_branch.html", {"error": "Failed to update branch"}
            )

        if "errors" in response_data:
            print(f"GraphQL errors: {response_data['errors']}")
            return render(
                request,
                "update_branch.html",
                {"error": response_data["errors"][0]["message"]},
            )

        if "data" in response_data and "updateBranch" in response_data["data"]:
            updated_branch = response_data["data"]["updateBranch"]["branch"]
            print(f"Updated Branch: {updated_branch}")
            return redirect("branch_list")

        else:
            print("Error: No branch data returned from GraphQL.")
            return render(
                request, "update_branch.html", {"error": "Failed to update branch"}
            )

    return render(request, "branch/update_branch.html", {"branch": branch})

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
        fetch_graphql_data(mutation, variables)
        return redirect("branch_list")  # Redirect to the branch list after deletion

    return render(
        request, "branch/delete_branch.html", {"branch_id": branch_id}
    )  # Render a confirmation page for deletion

def index(request):
    # Fetch the count of Baraas
    baraa_query = """
    query {
        baraas {
            baraaId
        }
    }
    """
    baraa_data = fetch_graphql_data(baraa_query)
    baraa_count = len(baraa_data.get("data", {}).get("baraas", []))

    # Fetch the count of Turuls
    turul_query = """
    query {
        turuls {
            turulId
        }
    }
    """
    turul_data = fetch_graphql_data(turul_query)
    turul_count = len(turul_data.get("data", {}).get("turuls", []))

    # Fetch the count of Workers
    worker_query = """
    query {
        workers {
            workerId
        }
    }
    """
    worker_data = fetch_graphql_data(worker_query)
    worker_count = len(worker_data.get("data", {}).get("workers", []))

    # Pass the counts to the template
    return render(request, "index.html", {
        "baraa_count": baraa_count,
        "turul_count": turul_count,
        "worker_count": worker_count,
    })

def signin(request):
    return render(request, "signin.html")

def register(request):
    return render(request, "register.html")


def products(request):
    query = """
    query BaraaListQuery {
        baraas {
            baraaId
            baraaName
            img
            description
            stock
            isAvailable
            mashinMark
            turul
            baraaUne
  }
}
    """
    data = fetch_graphql_data(query)

    if data and "data" in data and "baraas" in data["data"]:
        baraa_data = data["data"]["baraas"]
        print(baraa_data)  # Debugging line to check the structure
    else:
        baraa_data = []  # Default to empty list if no data

    return render(request, "baraa/products.html", {"baraas": baraa_data})

# baraas crud
def create_baraa(request):
    # Fetch turuls for the dropdown
    turul_query = """
    query {
        turuls {
            turulId
            turulName
        }
    }
    """
    turul_data = fetch_graphql_data(turul_query)
    turuls = turul_data.get("data", {}).get("turuls", [])

    if request.method == "POST":
        baraa_name = request.POST.get("baraaName")
        baraa_une = request.POST.get("baraaUne")
        mashin_mark = request.POST.get("mashinMark")
        img = request.FILES.get("img")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        is_available = request.POST.get("isAvailable") == 'true'  # Convert to boolean
        turul_id = request.POST.get("turulId")  # Get the turul_id from the form

        # Convert image to base64 if provided
        base64_img = None
        if img:
            file_content = img.read()
            base64_img = base64.b64encode(file_content).decode("utf-8")

        mutation = """
        mutation CreateBaraa($baraaName: String!, $baraaUne: Int!, $mashinMark: String!, $img: String, $description: String, $stock: Int, $isAvailable: Boolean, $turulId: Int!) {
            createBaraa(baraaName: $baraaName, baraaUne: $baraaUne, mashinMark: $mashinMark, img: $img, description: $description, stock: $stock, isAvailable: $isAvailable, turulId: $turulId) {
                baraa {
                    baraaId
                    baraaName
                    img
                    description
                    stock
                    isAvailable
                    mashinMark
                    slug
                }
            }
        }
        """

        variables = {
            "baraaName": baraa_name,
            "baraaUne": baraa_une,
            "mashinMark": mashin_mark,
            "img": base64_img,  # Send base64 encoded image
            "description": description,
            "stock": stock,
            "isAvailable": is_available,
            "turulId": turul_id,  # Include turul_id in the variables
        }

        response_data = fetch_graphql_data(mutation, variables)

        if response_data is None:
            return render(
                request, "create_baraa.html", {"error": "Failed to create Baraa", "turuls": turuls}
            )

        if "errors" in response_data:
            return render(
                request,
                "create_baraa.html",
                {"error": response_data["errors"][0]["message"], "turuls": turuls},
            )

        if "data" in response_data and "createBaraa" in response_data["data"]:
            return redirect("baraa_list")  # Redirect to the list of Baraas
        else:
            return render(
                request, "create_baraa.html", {"error": "Failed to create Baraa", "turuls": turuls}
            )

    return render(request, "baraa/create_baraa.html", {"turuls": turuls})

def settings(request):
    return render(request, "settings.html")

def report(request):
    return render(request, "report.html")

def notifications(request):
    return render(request, "notifications.html")

def worker_list(request):
    """
    View to fetch and display the list of workers.
    """
    query = """
    query {
        workers {
            workerId
            firstname
            lastname
            age
            img
            geriinhayg
            utasdugaar
            position
            salary
            branch {
                branchId
                branchName
            }
        }
    }
    """
    data = fetch_graphql_data(query)

    if data and "data" in data and "workers" in data["data"]:
        workers = data["data"]["workers"]
    else:
        workers = []  # Default to an empty list if no data is returned

    return render(request, "worker/worker.html", {"workers": workers})
# worker crud
def create_worker(request):
    """
    View to handle the creation of a new worker.
    """
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        age = request.POST.get("age")
        geriinhayg = request.POST.get("geriinhayg")
        utasdugaar = request.POST.get("utasdugaar")
        position = request.POST.get("position")
        salary = request.POST.get("salary")
        branch_id = request.POST.get("branch_id")
        img = request.FILES.get("img")  # Image uploaded by user

        # Convert image to Base64 string if provided
        base64_img = None
        if img:
            file_content = img.read()
            base64_img = base64.b64encode(file_content).decode("utf-8")

        mutation = """
        mutation CreateWorker(
            $firstname: String!, 
            $lastname: String!, 
            $position: String!, 
            $salary: Float!, 
            $branchId: Int!, 
            $img: String, 
            $age: Int, 
            $geriinhayg: String, 
            $utasdugaar: String
        ) {
            createWorker(
                firstname: $firstname, 
                lastname: $lastname, 
                position: $position, 
                salary: $salary, 
                branchId: $branchId, 
                img: $img, 
                age: $age, 
                geriinhayg: $geriinhayg, 
                utasdugaar: $utasdugaar
            ) {
                worker {
                    firstname
                    lastname
                    position
                    salary
                    branch {
                        branchId
                        branchName
                    }
                }
            }
        }
        """
        variables = {
            "firstname": firstname,
            "lastname": lastname,
            "age": int(age) if age else None,
            "geriinhayg": geriinhayg,
            "utasdugaar": utasdugaar,
            "position": position,
            "salary": float(salary),
            "branchId": int(branch_id),
            "img": base64_img,
        }

        response_data = fetch_graphql_data(mutation, variables)

        if response_data is None:
            return render(request, "worker/create_worker.html", {"error": "Failed to create worker"})

        if "errors" in response_data:
            return render(
                request,
                "worker/create_worker.html",
                {"error": response_data["errors"][0]["message"]},
            )

        if "data" in response_data and "createWorker" in response_data["data"]:
            return redirect("worker_list")
        else:
            return render(request, "worker/create_worker.html", {"error": "Failed to create worker"})

    # Fetch branches for the dropdown
    branch_query = """
    query {
        branches {
            branchId
            branchName
        }
    }
    """
    branch_data = fetch_graphql_data(branch_query)
    branches = branch_data.get("data", {}).get("branches", [])

    return render(request, "worker/create_worker.html", {"branches": branches})

def delete_worker(request, worker_id):
    if request.method == "POST":
        mutation = """
         mutation DeleteWorker($workerId: Int!) {
             deleteWorker(workerId: $workerId) {
                 success
             }
         }
         """
        variables = {"workerId": worker_id}
        fetch_graphql_data(mutation, variables)
        return redirect("worker_list")  # Redirect to the branch list after deletion

    return render(
        request, "worker/delete_worker.html", {"worker_id": worker_id}
    ) 

def update_worker(request, worker_id):
    worker = fetch_worker_by_id(worker_id)  # Implement this function to get worker details
    """
    View to handle the update of an existing worker.
    """
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        age = request.POST.get("age")
        geriinhayg = request.POST.get("geriinhayg")
        utasdugaar = request.POST.get("utasdugaar")
        position = request.POST.get("position")
        salary = request.POST.get("salary")
        branch_id = request.POST.get("branch_id")
        img = request.FILES.get("img")  # Image uploaded by user

        # Convert image to Base64 string if provided
        base64_img = None
        if img:
            file_content = img.read()  # Read the file content
            base64_img = base64.b64encode(file_content).decode(
                "utf-8"
            )

        mutation = """
        mutation UpdateWorker(
            $workerId: Int!, 
            $firstname: String!, 
            $lastname: String!, 
            $age: Int, 
            $img: String, 
            $geriinhayg: String, 
            $utasdugaar: String, 
            $position: String!, 
            $salary: Float!, 
            $branchId: Int!
        ) {
            updateWorker(
                workerId: $workerId, 
                firstname: $firstname, 
                lastname: $lastname, 
                age: $age, 
                img: $img, 
                geriinhayg: $geriinhayg, 
                utasdugaar: $utasdugaar, 
                position: $position, 
                salary: $salary, 
                branchId: $branchId
            ) {
                worker {
                    workerId
                    firstname
                    lastname
                    position
                    salary
                    branch {
                        branchId
                        branchName
                    }
                }
            }
        }
        """
        
        variables = {
            "workerId": worker_id,
            "firstname": firstname,
            "lastname": lastname,
            "age": int(age) if age else None,
            "img": base64_img,
            "geriinhayg": geriinhayg,
            "utasdugaar": utasdugaar,
            "position": position,
            "salary": float(salary),
            "branchId": int(branch_id),
        }

        response_data = fetch_graphql_data(mutation, variables)

        if response_data is None:
            return render(request, "worker/update_worker.html", {"error": "Failed to update worker"})

        if "errors" in response_data:
            return render(
                request,
                "worker/update_worker.html",
                {"error": response_data["errors"][0]["message"]},
            )

        if "data" in response_data and "updateWorker" in response_data["data"]:
            return redirect("worker_list")  # Redirect to the worker list after updating
        else:
            return render(request, "worker/update_worker.html", {"error": "Failed to update worker"})

    # Fetch the current worker data to prepopulate the form
    if worker is None:
        return render(request, "worker/update_worker.html", {"error": "Worker not found"})

    # Fetch branches for the dropdown (if needed)
    branch_query = """
    query {
        branches {
            branchId
            branchName
        }
    }
    """
    branch_data = fetch_graphql_data(branch_query)
    branches = branch_data.get("data", {}).get("branches", [])

    return render(request, "worker/update_worker.html", {"worker": worker, "branches": branches})

def fetch_worker_by_id(worker_id):
    query = """
    query WorkerQuery($workerId: Int!) {
        worker(workerId: $workerId) {
            workerId
            firstname
            lastname
            age
            img
            position
            salary
            slug
            geriinhayg
            utasdugaar
            branch {
                branchId
                branchName
            }
        }
    }
    """
    variables = {"workerId": worker_id}
    response_data = fetch_graphql_data(query, variables)  # Implement this function to execute the query
    return response_data.get('data', {}).get('worker', None) if response_data else None


def fetch_turul_by_id(turul_id):
    """
    Fetch turul details by turul_id using a GraphQL query.
    """
    query = """
    query FetchTurulById($turulId: Int!) {
        turuls(turulId: $turulId) {
            turulId
            turulName
            description
            img
            slug
        }
    }
    """
    variables = {"turulId": turul_id}
    response = requests.post(
        GRAPHQL_ENDPOINT,
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        turuls = data.get("data", {}).get("turuls", [])
        return turuls[0] if turuls else None
    else:
        raise Exception(
            f"Failed to fetch turul. Status code: {response.status_code}, Response: {response.text}"
        )

def fetch_turuls():
    query = """
    query {
        turuls {
            turulId
            turulName
        }
    }
    """
    response = requests.post(
        GRAPHQL_ENDPOINT, 
        json={'query': query}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("turuls", [])
    else:
        return []

def turul_list(request):
    query = """
    query TurulListQuery {
      turuls {
        turulId
        turulName
        description
        img
      }
    }
    """
    data = fetch_graphql_data(query)

    if data and "data" in data and "turuls" in data["data"]:
        turul_data = data["data"]["turuls"]
        print(turul_data)  # Debugging line to check the structure
    else:
        turul_data = []  # Default to empty list if no data

    return render(request, "turul/turul.html", {"turuls": turul_data})


def create_turul(request):
    if request.method == "POST":
        turul_name = request.POST.get("turulName")
        description = request.POST.get("description")
        img = request.FILES.get("img")

        # Convert image to base64 if provided
        base64_img = None
        if img:
            file_content = img.read()
            base64_img = base64.b64encode(file_content).decode("utf-8")

        mutation = """
        mutation CreateTurul($turulName: String!, $description: String, $img: String) {
            createTurul(turulName: $turulName, description: $description, img: $img) {
                turul {
                    turulId
                    turulName
                    description
                    img
                    slug
                }
            }
        }
        """

        variables = {
            "turulName": turul_name,
            "description": description,
            "img": base64_img,  # Send base64 encoded image
        }

        response_data = fetch_graphql_data(mutation, variables)

        if response_data is None:
            return render(request, "turul/create_turul.html", {"error": "Failed to create turul"})

        if "errors" in response_data:
            return render(request, "turul/create_turul.html", {"error": response_data["errors"][0]["message"]})

        if "data" in response_data and "createTurul" in response_data["data"]:
            return redirect("turul_list")
        else:
            return render(request, "turul/create_turul.html", {"error": "Failed to create turul"})

    return render(request, "turul/create_turul.html")

def update_turul(request, turul_id):
    # Fetch the turul data to prepopulate the form
    turul = fetch_turul_by_id(turul_id)

    if request.method == "POST":
        turul_name = request.POST.get("turulName")
        description = request.POST.get("description")
        img = request.FILES.get("img")  # Access the uploaded image file

        # Convert the image file to a Base64-encoded string if provided
        base64_img = None
        if img:
            file_content = img.read()  # Read the file content
            base64_img = base64.b64encode(file_content).decode(
                "utf-8"
            )  # Encode to Base64

        # Prepare the GraphQL mutation and variables
        mutation = """
        mutation UpdateTurul($turulId: Int!, $turulName: String, $description: String, $img: String) {
            updateTurul(turulId: $turulId, turulName: $turulName, description: $description, img: $img) {
                turul {
                    turulId
                    turulName
                    slug
                    img
                    description
                }
            }
        }
        """
        variables = {
            "turulId": turul_id,
            "turulName": turul_name,
            "description": description,
            "img": base64_img,  # Include the Base64-encoded image
        }

        # Fetch mutation response
        response_data = fetch_graphql_data(mutation, variables)

        if response_data is None:
            print("Error: No valid response from the server.")
            return render(
                request, "turul/update_turul.html", {"error": "Failed to update turul"}
            )

        if "errors" in response_data:
            print(f"GraphQL errors: {response_data['errors']}")
            return render(
                request,
                "turul/update_turul.html",
                {"error": response_data["errors"][0]["message"]},
            )

        if "data" in response_data and "updateTurul" in response_data["data"]:
            updated_turul = response_data["data"]["updateTurul"]["turul"]
            print(f"Updated Turul: {updated_turul}")
            return redirect("turul_list")

        else:
            print("Error: No turul data returned from GraphQL.")
            return render(
                request, "turul/update_turul.html", {"error": "Failed to update turul"}
            )

    return render(request, "turul/update_turul.html", {"turul": turul})

def delete_turul(request, turul_id):
    if request.method == "POST":
        mutation = """
        mutation DeleteTurul($turulId: Int!) {
          deleteTurul(turulId: $turulId) {
            success
          }
        }
        """
        variables = {"turulId": turul_id}
        fetch_graphql_data(mutation, variables)
        return redirect("turul_list")  # Redirect to the turul list after deletion

    return render(
        request, "turul/delete_turul.html", {"turul_id": turul_id}
    )  # Render a confirmation page for deletion


