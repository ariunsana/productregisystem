from django.db import models
from slugify import slugify

class Turul(models.Model):
    turul_id = models.AutoField(primary_key=True)
    turul_name = models.CharField(max_length=100, null=False)
    img = models.ImageField(upload_to='photos/turul', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.turul_name

class Baraa(models.Model):
    baraa_id = models.AutoField(primary_key=True)
    baraa_name = models.CharField(max_length=100, null=False)
    baraa_une = models.IntegerField(null=False)
    slug = models.SlugField(max_length=100, unique=True, null=False)
    mashin_mark = models.CharField(max_length=50, null=False)
    img = models.ImageField(upload_to='photos/baraa', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    turul = models.ForeignKey(Turul, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.baraa_name


class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=100, null=False)
    img = models.ImageField(upload_to='photos/branch', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, null=False)
    branch_location = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.branch_name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.branch_name


class BranchBaraa(models.Model):
    sector_id = models.IntegerField(null=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    baraa = models.ForeignKey(Baraa, on_delete=models.CASCADE)
    item_count = models.IntegerField(default=0, null=False)

    class Meta:
        unique_together = ('sector_id', 'baraa')

    def __str__(self):
        return f"Sector {self.sector_id}, Branch {self.branch.branch_name}, Item {self.baraa.baraa_name}"


class UserRole(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100, unique=True, null=False)
    slug = models.SlugField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.role_name


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True, null=False)
    passwd = models.CharField(max_length=50, null=False)  # For hashed passwords
    status = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True, null=False)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, null=False)
    slug = models.SlugField(max_length=100, unique=True, null=False)
    create_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Worker(models.Model):
    worker_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50, null=False)
    lastname = models.CharField(max_length=50, null=False)
    age = models.IntegerField(blank=True, null=True)
    img = models.ImageField(upload_to='photos/worker', blank=True, null=True)
    geriinhayg = models.TextField(blank=True, null=True)
    utasdugaar = models.CharField(max_length=15, blank=True, null=True)  # Adjusted for phone number format
    position = models.CharField(max_length=50, null=False)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    slug = models.SlugField(max_length=100, unique=True, null=False)
    start_date = models.DateField(auto_now_add=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.firstname)
        super().save(*args, **kwargs)

class Sales(models.Model):
    sales_id = models.AutoField(primary_key=True)
    sale_date = models.DateTimeField(auto_now_add=True, null=False)
    baraa = models.ForeignKey(Baraa, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField(null=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=False)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, null=False)

    def __str__(self):
        return f"Sale ID: {self.sales_id}"


class Supply(models.Model):
    supply_id = models.AutoField(primary_key=True)
    baraa = models.ForeignKey(Baraa, on_delete=models.CASCADE, null=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=False)
    supply_date = models.DateTimeField(auto_now_add=True, null=False)
    supplied_quantity = models.IntegerField(null=False)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"Supply {self.supply_id} for {self.baraa.baraa_name}"
