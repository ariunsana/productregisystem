import graphene
from graphene_django.types import DjangoObjectType
from .models import *
from slugify import slugify
import base64
from graphql import GraphQLError
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.text import slugify
from django.conf import settings
from graphene import Mutation, Field, String
import os

# Define Types for all models
class TurulType(DjangoObjectType):
    class Meta:
        model = Turul
class BaraaType(DjangoObjectType):
    class Meta:
        model = Baraa
class BranchType(DjangoObjectType):
    class Meta:
        model = Branch
class BranchBaraaType(DjangoObjectType):
    class Meta:
        model = BranchBaraa
class UserRoleType(DjangoObjectType):
    class Meta:
        model = UserRole
class UsersType(DjangoObjectType):
    class Meta:
        model = Users
class WorkerType(DjangoObjectType):
    class Meta:
        model = Worker
class SalesType(DjangoObjectType):
    class Meta:
        model = Sales
class SupplyType(DjangoObjectType):
    class Meta:
        model = Supply

# Input Types for Registration and Login
class RegisterInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    confirm_password = graphene.String(required=True)
    role_name = graphene.String(required=True)
class LoginInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)

# Types
class BranchType(graphene.ObjectType):
    branch_id = graphene.Int()
    branch_name = graphene.String()
    img = graphene.String()
    slug = graphene.String()
    branch_location = graphene.String()

class TurulType(graphene.ObjectType):
    turul_id = graphene.Int()
    turul_name = graphene.String()
    img = graphene.String()
    slug = graphene.String()
    description = graphene.String()

class BaraaType(graphene.ObjectType):
    baraa_id = graphene.Int()
    baraa_name = graphene.String()
    baraa_une = graphene.Float()
    img = graphene.String()
    stock = graphene.Int()
    is_available = graphene.Boolean()  # Added the is_available field
    description = graphene.String()
    mashin_mark = graphene.String()
    turul = graphene.String()




class UserType(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    role_name = graphene.String()
    access_token = graphene.String()

class UserRoleType(graphene.ObjectType):
    role_id = graphene.ID()
    role_name = graphene.String()
    slug = graphene.String()


# Mutations for Registration and Login
class RegisterUser(graphene.Mutation):
    class Arguments:
        input = RegisterInput(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, input):
        # Check if user or email exists
        if Users.objects.filter(username=input.username).exists():
            raise GraphQLError("Username already exists.")
        if Users.objects.filter(email=input.email).exists():
            raise GraphQLError("Email already exists.")

        # Check if passwords match
        if input.password != input.confirm_password:
            raise GraphQLError("Passwords do not match.")

        # Fetch Role
        role = UserRole.objects.filter(role_name=input.role_name).first()
        if not role:
            raise GraphQLError("Role not found.")

        # Create user
        user = Users.objects.create(
            username=input.username,
            email=input.email,
            passwd=make_password(input.password),
            role=role
        )

        return RegisterUser(user=user)


class LoginUser(graphene.Mutation):
    class Arguments:
        input = LoginInput(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, input):
        try:
            user = Users.objects.get(username=input.username)
        except Users.DoesNotExist:
            raise GraphQLError("Invalid username or password.")

        if not check_password(input.password, user.passwd):
            raise GraphQLError("Invalid username or password.")

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return LoginUser(user=UserType(
            id=user.user_id,
            username=user.username,
            email=user.email,
            role_name=user.role.role_name,
            access_token=access_token
        ))

# Define Query for all models
class Query(graphene.ObjectType):
    # Query all models
    turuls = graphene.List(TurulType, turul_id=graphene.Int())
    baraas = graphene.List(BaraaType, baraa_id=graphene.Int())
    branches = graphene.List(BranchType, branch_id=graphene.Int())
    branch_baraas = graphene.List(BranchBaraaType)
    user_roles = graphene.List(UserRoleType)
    users = graphene.List(UsersType)
    sales = graphene.List(SalesType)
    supplies = graphene.List(SupplyType)
    workers = graphene.List(WorkerType) 
    worker = graphene.Field(WorkerType, worker_id=graphene.Int())

    def resolve_workers(self, info, **kwargs):
        return Worker.objects.all()

    def resolve_worker(self, info, worker_id, **kwargs):
        try:
            return Worker.objects.get(pk=worker_id)
        except Worker.DoesNotExist:
            return None

    # Define resolvers
    def resolve_turuls(self, info, turul_id=None, **kwargs):
        if turul_id:
            # If turul_id is provided, filter by turul_id
            return Turul.objects.filter(pk=turul_id)
        else:
            # Otherwise, return all turuls
            return Turul.objects.all()

    # def resolve_baraas(self, info, **kwargs):
    #     return Baraa.objects.all()

    def resolve_baraas(self, info, baraa_id=None, **kwargs):
        if baraa_id is not None:
            return Baraa.objects.filter(pk=baraa_id)
        return Baraa.objects.all()
        
    def resolve_branches(self, info, branch_id=None, **kwargs):
        if branch_id:
            # If branch_id is provided, filter by branch_id
            return Branch.objects.filter(pk=branch_id)
        else:
            # Otherwise, return all branches
            return Branch.objects.all()
        
    def resolve_branch_baraas(self, info, **kwargs):
        return BranchBaraa.objects.all()

    def resolve_user_roles(self, info, **kwargs):
        return UserRole.objects.all()

    def resolve_users(self, info, **kwargs):
        return Users.objects.all()

    def resolve_sales(self, info, **kwargs):
        return Sales.objects.all()

    def resolve_supplies(self, info, **kwargs):
        return Supply.objects.all()

# Define Mutations for all models
class CreateTurul(graphene.Mutation):
    class Arguments:
        turul_name = graphene.String(required=True)
        description = graphene.String()
        img = graphene.String()  # Optional Base64-encoded image

    turul = Field(lambda: TurulType)

    def mutate(self, info, turul_name, description=None, img=None):
        # Generate the slug if not provided
        slug = slugify(turul_name)

        # Process image if provided
        image_path = None
        if img:
            try:
                # Decode the Base64 image
                decoded_image = base64.b64decode(img)
            except (TypeError, ValueError):
                raise ValueError("Invalid Base64-encoded image.")

            # Define the image directory and file path
            image_dir = os.path.join(settings.MEDIA_ROOT, "photos", "turul")
            os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
            image_filename = f"{turul_name}_turul.jpg"  # Using slug for the image filename
            image_path = os.path.join(image_dir, image_filename)

            # Save the image to the local file system
            with open(image_path, "wb") as image_file:
                image_file.write(decoded_image)

        # Create and save the Turul object
        turul = Turul(
            turul_name=turul_name,
            slug=slug,
            description=description,
            img=f"photos/turul/{os.path.basename(image_path)}" if image_path else None,
        )
        turul.save()

        return CreateTurul(turul=turul)

class UpdateTurul(graphene.Mutation):
    class Arguments:
        turul_id = graphene.Int(required=True)
        turul_name = graphene.String()
        description = graphene.String()
        img = graphene.String()  # Optional Base64-encoded image

    turul = Field(lambda: TurulType)

    def mutate(self, info, turul_id, turul_name=None, description=None, img=None):
        # Fetch the Turul object to update
        try:
            turul = Turul.objects.get(pk=turul_id)
        except Turul.DoesNotExist:
            raise ValueError("Turul with the given ID does not exist.")

        # Update fields if provided
        if turul_name:
            turul.turul_name = turul_name
            turul.slug = slugify(turul_name)  # Re-generate the slug if name is changed

        if description:
            turul.description = description

        # Process image if provided
        if img:
            try:
                # Decode the Base64 image
                decoded_image = base64.b64decode(img)
            except (TypeError, ValueError):
                raise ValueError("Invalid Base64-encoded image.")

            # Define the image directory and file path
            image_dir = os.path.join(settings.MEDIA_ROOT, "photos", "turul")
            os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
            image_filename = f"{turul.slug}_turul.jpg"  # Using the slug for the image filename
            image_path = os.path.join(image_dir, image_filename)

            # Save the new image to the local file system
            with open(image_path, "wb") as image_file:
                image_file.write(decoded_image)

            # Update the image path
            turul.img = f"photos/turul/{os.path.basename(image_path)}"

        # Save the updated Turul object
        turul.save()

        return UpdateTurul(turul=turul)

class DeleteTurul(graphene.Mutation):
    class Arguments:
        turul_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, turul_id):
        # Attempt to fetch the Turul object to delete
        try:
            turul = Turul.objects.get(pk=turul_id)
        except Turul.DoesNotExist:
            raise ValueError("Turul with the given ID does not exist.")

        # Delete the Turul object
        turul.delete()

        return DeleteTurul(success=True)

# CRUD operations for Baraa
class CreateBaraa(graphene.Mutation):
    class Arguments:
        baraa_name = graphene.String(required=True)
        baraa_une = graphene.Int(required=True)
        mashin_mark = graphene.String(required=True)
        img = graphene.String()  # Base64-encoded image
        description = graphene.String()
        stock = graphene.Int()
        is_available = graphene.Boolean()
        turul_id = graphene.String()

    baraa = graphene.Field(BaraaType)

    def mutate(self, info, baraa_name, baraa_une, mashin_mark, turul_id, img=None, description=None, stock=0, is_available=True,):
        # Generate the slug from the baraa_name
        slug = slugify(baraa_name)

        # Prepare the image file if provided
        image_path = None
        if img:
            try:
                # Decode the Base64 image
                decoded_image = base64.b64decode(img)
            except (TypeError, ValueError):
                raise ValueError("Invalid Base64-encoded image.")

            # Define the image directory and file path
            image_dir = os.path.join(settings.MEDIA_ROOT, "photos", "baraa")
            os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
            image_filename = f"{slug}_baraa.jpg"  # Use slug for the image filename
            image_path = os.path.join(image_dir, image_filename)

            # Save the image to the local file system
            with open(image_path, "wb") as image_file:
                image_file.write(decoded_image)

        # Create a new Baraa instance
        baraa = Baraa(
            baraa_name=baraa_name,
            baraa_une=baraa_une,
            mashin_mark=mashin_mark,
            img=f"photos/baraa/{os.path.basename(image_path)}" if image_path else None,
            description=description,
            stock=stock,
            is_available=is_available,
            slug=slug,  # Ensure slug is included
        )

        # Save the baraa to the database
        baraa.save()

        return CreateBaraa(baraa=baraa)

class UpdateBaraa(graphene.Mutation):
    class Arguments:
        baraa_id = graphene.Int(required=True)
        baraa_name = graphene.String()
        baraa_une = graphene.Int()
        slug = graphene.String()
        mashin_mark = graphene.String()
        img = graphene.String()
        description = graphene.String()
        stock = graphene.Int()
        is_available = graphene.Boolean()

    baraa = graphene.Field(BaraaType)

    def mutate(self, info, baraa_id, baraa_name=None, baraa_une=None, slug=None, mashin_mark=None, img=None, description=None, stock=None, is_available=None):
        baraa = Baraa.objects.get(pk=baraa_id)
        if baraa_name:
            baraa.baraa_name = baraa_name
        if baraa_une:
            baraa.baraa_une = baraa_une
        if slug:
            baraa.slug = slug
        if mashin_mark:
            baraa.mashin_mark = mashin_mark
        if img:
            baraa.img = img
        if description:
            baraa.description = description
        if stock is not None:
            baraa.stock = stock
        if is_available is not None:
            baraa.is_available = is_available
        baraa.save()
        return UpdateBaraa(baraa=baraa)

class DeleteBaraa(graphene.Mutation):
    class Arguments:
        baraa_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, baraa_id):
        baraa = Baraa.objects.get(pk=baraa_id)
        baraa.delete()
        return DeleteBaraa(success=True)

# Example for Branch

class CreateBranch(Mutation):
    class Arguments:
        branch_name = String(required=True)
        img = String()  # Base64-encoded image
        branch_location = String()
    branch = Field(lambda: BranchType)

    def mutate(self, info, branch_name, img=None, branch_location=None):
        # Generate the slug from the branch_name
        slug = slugify(branch_name)

        # Prepare the image file if provided
        image_path = None
        if img:
            try:
                # Decode the Base64 image
                decoded_image = base64.b64decode(img)
            except (TypeError, ValueError):
                raise ValueError("Invalid Base64-encoded image.")

            # Define the image directory and file path
            image_dir = os.path.join(settings.MEDIA_ROOT, "photos", "branch")
            os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
            image_filename = f"{branch_name}_branch.jpg"
            image_path = os.path.join(image_dir, image_filename)

            # Save the image to the local file system
            with open(image_path, "wb") as image_file:
                image_file.write(decoded_image)

        # Create a new Branch instance
        branch = Branch(
            branch_name=branch_name,
            img=f"photos/branch/{os.path.basename(image_path)}" if image_path else None,
            branch_location=branch_location,
            slug=slug,
        )

        # Save the branch to the database
        branch.save()

        return CreateBranch(branch=branch)

class UpdateBranch(Mutation):
    class Arguments:
        branch_id = graphene.Int(required=True)  # The ID of the branch to update
        branch_name = graphene.String()  # Optional field for updating the name
        img = graphene.String()  # Optional Base64-encoded image
        branch_location = graphene.String()  # Optional field for updating location

    branch = Field(lambda: BranchType)

    def mutate(self, info, branch_id, branch_name=None, img=None, branch_location=None):
        # Fetch the branch instance to update
        try:
            branch = Branch.objects.get(pk=branch_id)
        except Branch.DoesNotExist:
            raise ValueError("Branch with the given ID does not exist.")

        # Update branch_name and slug if branch_name is provided
        if branch_name:
            branch.branch_name = branch_name
            branch.slug = slugify(branch_name)  # Generate a new slug

        # Update img if provided
        if img:
            try:
                # Decode the Base64 image
                decoded_image = base64.b64decode(img)
            except (TypeError, ValueError):
                raise ValueError("Invalid Base64-encoded image.")

            # Define the image directory and file path
            image_dir = os.path.join(settings.MEDIA_ROOT, "photos", "branch")
            os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
            image_filename = f"{branch.slug}_branch.jpg"  # Use slug for the image filename
            image_path = os.path.join(image_dir, image_filename)

            # Save the new image to the local file system
            with open(image_path, "wb") as image_file:
                image_file.write(decoded_image)

            # Update the image path in the branch instance
            branch.img = f"photos/branch/{os.path.basename(image_path)}"

        # Update branch_location if provided
        if branch_location:
            branch.branch_location = branch_location

        # Save the updated branch instance
        branch.save()

        return UpdateBranch(branch=branch)


class DeleteBranch(graphene.Mutation):
    class Arguments:
        branch_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, branch_id):
        branch = Branch.objects.get(pk=branch_id)
        branch.delete()
        return DeleteBranch(success=True)

# CRUD operations for BranchBaraa
class CreateBranchBaraa(graphene.Mutation):
    class Arguments:
        sector_id = graphene.Int(required=True)
        branch_id = graphene.Int(required=True)
        baraa_id = graphene.Int(required=True)
        item_count = graphene.Int()

    branch_baraa = graphene.Field(BranchBaraaType)

    def mutate(self, info, sector_id, branch_id, baraa_id, item_count=0):
        branch = Branch.objects.get(pk=branch_id)
        baraa = Baraa.objects.get(pk=baraa_id)
        branch_baraa = BranchBaraa(sector_id=sector_id, branch=branch, baraa=baraa, item_count=item_count)
        branch_baraa.save()
        return CreateBranchBaraa(branch_baraa=branch_baraa)

class UpdateBranchBaraa(graphene.Mutation):
    class Arguments:
        sector_id = graphene.Int(required=True)
        item_count = graphene.Int()

    branch_baraa = graphene.Field(BranchBaraaType)

    def mutate(self, info, sector_id, item_count):
        branch_baraa = BranchBaraa.objects.get(sector_id=sector_id)
        branch_baraa.item_count = item_count
        branch_baraa.save()
        return UpdateBranchBaraa(branch_baraa=branch_baraa)

class DeleteBranchBaraa(graphene.Mutation):
    class Arguments:
        sector_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, sector_id):
        branch_baraa = BranchBaraa.objects.get(sector_id=sector_id)
        branch_baraa.delete()
        return DeleteBranchBaraa(success=True)

# CRUD operations for UserRole
class CreateUserRole(graphene.Mutation):
    class Arguments:
        role_name = graphene.String(required=True)
        slug = graphene.String(required=True)

    user_role = graphene.Field(UserRoleType)

    def mutate(self, info, role_name, slug):
        user_role = UserRole(role_name=role_name, slug=slug)
        user_role.save()
        return CreateUserRole(user_role=user_role)

class UpdateUserRole(graphene.Mutation):
    class Arguments:
        role_id = graphene.Int(required=True)
        role_name = graphene.String()
        slug = graphene.String()

    user_role = graphene.Field(UserRoleType)

    def mutate(self, info, role_id, role_name=None, slug=None):
        user_role = UserRole.objects.get(pk=role_id)
        if role_name:
            user_role.role_name = role_name
        if slug:
            user_role.slug = slug
        user_role.save()
        return UpdateUserRole(user_role=user_role)

class DeleteUserRole(graphene.Mutation):
    class Arguments:
        role_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, role_id):
        user_role = UserRole.objects.get(pk=role_id)
        user_role.delete()
        return DeleteUserRole(success=True)

# CRUD operations for Users
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        passwd = graphene.String(required=True)
        email = graphene.String(required=True)
        role_id = graphene.Int(required=True)
        slug = graphene.String(required=True)

    user = graphene.Field(UsersType)

    def mutate(self, info, username, passwd, email, role_id, slug):
        role = UserRole.objects.get(pk=role_id)
        user = Users(username=username, passwd=passwd, email=email, role=role, slug=slug)
        user.save()
        return CreateUser(user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        username = graphene.String()
        passwd = graphene.String()
        email = graphene.String()
        role_id = graphene.Int()
        slug = graphene.String()

    user = graphene.Field(UsersType)

    def mutate(self, info, user_id, username=None, passwd=None, email=None, role_id=None, slug=None):
        user = Users.objects.get(pk=user_id)
        if username:
            user.username = username
        if passwd:
            user.passwd = passwd
        if email:
            user.email = email
        if role_id:
            user.role = UserRole.objects.get(pk=role_id)
        if slug:
            user.slug = slug
        user.save()
        return UpdateUser(user=user)

class DeleteUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, user_id):
        user = Users.objects.get(pk=user_id)
        user.delete()
        return DeleteUser(success=True)
    

# CRUD operations for Worker
class CreateWorker(graphene.Mutation):
    class Arguments:
        firstname = graphene.String(required=True)
        lastname = graphene.String(required=True)
        age = graphene.Int()
        img = graphene.String()  # Path or base64 string can be used
        geriinhayg = graphene.String()
        utasdugaar = graphene.String()
        position = graphene.String(required=True)
        salary = graphene.Float(required=True)
        branch_id = graphene.Int(required=True)

    worker = graphene.Field(WorkerType)
    def mutate(self, info, firstname, lastname, position, salary, branch_id, img, age,geriinhayg,utasdugaar):
        slug = slugify(firstname)
        try:
            branch = Branch.objects.get(pk=branch_id)
        except Branch.DoesNotExist:
            raise Exception("Branch does not exist")
        image_path = None
        if img:
            try:
                # Decode the Base64 image
                decoded_image = base64.b64decode(img)
            except (TypeError, ValueError):
                raise ValueError("Invalid Base64-encoded image.")

            # Define the image directory and file path
            image_dir = os.path.join(settings.MEDIA_ROOT, "photos", "worker")
            os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
            image_filename = f"{firstname}_{lastname}_worker.jpg"
            image_path = os.path.join(image_dir, image_filename)

            # Save the image to the local file system
            with open(image_path, "wb") as image_file:
                image_file.write(decoded_image)
        worker = Worker(
            firstname=firstname,
            lastname=lastname,
            age=age,
            img=f"photos/worker/{os.path.basename(image_path)}" if image_path else None,
            geriinhayg=geriinhayg,
            utasdugaar=utasdugaar,
            position=position,
            slug=slug,
            salary=salary,
            branch=branch
        )

        worker.save()
        return CreateWorker(worker=worker)
    
class UpdateWorker(graphene.Mutation):
    class Arguments:
        worker_id = graphene.Int(required=True)  # ID of the worker to update
        firstname = graphene.String(required=True)
        lastname = graphene.String(required=True)
        age = graphene.Int()
        img = graphene.String()  # Path or base64 string can be used
        geriinhayg = graphene.String()
        utasdugaar = graphene.String()
        position = graphene.String(required=True)
        salary = graphene.Float(required=True)
        branch_id = graphene.Int(required=True)

    worker = graphene.Field(WorkerType)

    def mutate(self, info, worker_id, firstname, lastname, position, salary, branch_id, img=None, age=None, geriinhayg=None, utasdugaar=None):
        try:
            worker = Worker.objects.get(pk=worker_id)
        except Worker.DoesNotExist:
            raise Exception("Worker does not exist")

        # Update fields
        worker.firstname = firstname
        worker.slug = slugify(firstname)
        worker.lastname = lastname
        worker.position = position
        worker.salary = salary
        worker.age = age
        worker.geriinhayg = geriinhayg
        worker.utasdugaar = utasdugaar

        # Update branch
        try:
            branch = Branch.objects.get(pk=branch_id)
            worker.branch = branch
        except Branch.DoesNotExist:
            raise Exception("Branch does not exist")

        # Handle image update
        if img is not None:
            if img.startswith('data:image/'):  # Check if it's a base64 string
                try:
                    # Decode the Base64 image
                    decoded_image = base64.b64decode(img.split(',')[1])  # Remove the prefix
                except (TypeError, ValueError):
                    raise ValueError("Invalid Base64-encoded image.")

                # Define the image directory and file path
                image_dir = os.path.join(settings.MEDIA_ROOT, "photos", "worker")
                os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists
                image_filename = f"{firstname}_{lastname}_worker.jpg"
                image_path = os.path.join(image_dir, image_filename)

                # Save the image to the local file system
                with open(image_path, "wb") as image_file:
                    image_file.write(decoded_image)

                worker.img = f"photos/worker/{os.path.basename(image_path)}"  # Update the image path

        worker.slug = slugify(f"{firstname} {lastname}")  # Update slug based on name
        worker.save()  # Save the updated worker instance
        return UpdateWorker(worker=worker)

class DeleteWorker(graphene.Mutation):
    class Arguments:
        worker_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, worker_id):
        try:
            worker = Worker.objects.get(pk=worker_id)
            worker.delete()
            return DeleteWorker(success=True)
        except Worker.DoesNotExist:
            raise ValueError("Worker with the given ID does not exist.")

# CRUD operations for Sales
class CreateSales(graphene.Mutation):
    class Arguments:
        baraa_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)
        branch_id = graphene.Int(required=True)
        worker_id = graphene.Int(required=True)
        total_price = graphene.Float(required=True)

    sales = graphene.Field(SalesType)

    def mutate(self, info, baraa_id, quantity, branch_id, worker_id, total_price):
        baraa = Baraa.objects.get(pk=baraa_id)
        branch = Branch.objects.get(pk=branch_id)
        worker = Worker.objects.get(pk=worker_id)
        sales = Sales(baraa=baraa, quantity=quantity, branch=branch, worker=worker, total_price=total_price)
        sales.save()
        return CreateSales(sales=sales)

class UpdateSales(graphene.Mutation):
    class Arguments:
        sales_id = graphene.Int(required=True)
        quantity = graphene.Int()
        total_price = graphene.Float()

    sales = graphene.Field(SalesType)

    def mutate(self, info, sales_id, quantity=None, total_price=None):
        sales = Sales.objects.get(pk=sales_id)
        if quantity is not None:
            sales.quantity = quantity
        if total_price is not None:
            sales.total_price = total_price
        sales.save()
        return UpdateSales(sales=sales)

class DeleteSales(graphene.Mutation):
    class Arguments:
        sales_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, sales_id):
        sales = Sales.objects.get(pk=sales_id)
        sales.delete()
        return DeleteSales(success=True)

# CRUD operations for Supply
class CreateSupply(graphene.Mutation):
    class Arguments:
        baraa_id = graphene.Int(required=True)
        branch_id = graphene.Int(required=True)
        supplied_quantity = graphene.Int(required=True)
        worker_id = graphene.Int(required=True)

    supply = graphene.Field(SupplyType)

    def mutate(self, info, baraa_id, branch_id, supplied_quantity, worker_id):
        baraa = Baraa.objects.get(pk=baraa_id)
        branch = Branch.objects.get(pk=branch_id)
        worker = Worker.objects.get(pk=worker_id)
        supply = Supply(baraa=baraa, branch=branch, supplied_quantity=supplied_quantity, worker=worker)
        supply.save()
        return CreateSupply(supply=supply)

class UpdateSupply(graphene.Mutation):
    class Arguments:
        supply_id = graphene.Int(required=True)
        supplied_quantity = graphene.Int()

    supply = graphene.Field(SupplyType)

    def mutate(self, info, supply_id, supplied_quantity=None):
        supply = Supply.objects.get(pk=supply_id)
        if supplied_quantity is not None:
            supply.supplied_quantity = supplied_quantity
        supply.save()
        return UpdateSupply(supply=supply)

class DeleteSupply(graphene.Mutation):
    class Arguments:
        supply_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, supply_id):
        supply = Supply.objects.get(pk=supply_id)
        supply.delete()
        return DeleteSupply(success=True)

# Root Mutation
class Mutation(graphene.ObjectType):
    create_user_role = CreateUserRole.Field()
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()

    # Include other mutations here (e.g., CRUD operations for other models)
    create_turul = CreateTurul.Field()
    update_turul = UpdateTurul.Field()
    delete_turul = DeleteTurul.Field()

    create_branch = CreateBranch.Field()
    update_branch = UpdateBranch.Field()
    delete_branch = DeleteBranch.Field()

    create_worker = CreateWorker.Field()
    update_worker = UpdateWorker.Field()
    delete_worker = DeleteWorker.Field()

    create_baraa = CreateBaraa.Field()
    # ... other mutations ...

# Create schema
schema = graphene.Schema(query=Query, mutation=Mutation)


