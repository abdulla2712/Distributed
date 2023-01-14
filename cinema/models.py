from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError

# Create your models here.

Group.add_to_class('is_active', models.BooleanField(default=True, verbose_name='active'))

class User(AbstractUser):
  phone = PhoneNumberField(null=True, blank=True, unique=True, default=None)
  salary = MoneyField(decimal_places=2, default=0, default_currency='GBP', max_digits=11)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class Theater(models.Model):
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True, verbose_name='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_screens(self, is_authenticated):
        if is_authenticated:
            return Screen.objects.filter(theater=self.id).order_by('name')
        else:
            return Screen.objects.filter(theater=self.id, is_active=True).order_by('name')


class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True, verbose_name='active')

    def __str__(self):
        return self.name

class Movie(models.Model):
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    name = models.CharField(max_length=200)
    starts_at = models.DateTimeField('start date', null=False, blank=False)
    ends_at = models.DateTimeField('end date', null=False, blank=False)
    is_active = models.BooleanField(editable=False, verbose_name='active')
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    def clean(self):
        if self.starts_at is not None and self.starts_at > self.ends_at:
            raise ValidationError('Start date is after end date.')
        if hasattr(self, 'category') and self.category.is_active == False:
            raise ValidationError('The category is not active.')

class Screen(models.Model):
    class Meta:
      unique_together = ('theater', 'name')

    VIP = 1
    PUBLIC = 2

    TYPE_CHOICES = (
        (VIP, 'VIP'),
        (PUBLIC, 'Public'),
    )

    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    total_seats = models.PositiveIntegerField(default=10, validators=[MinValueValidator(10), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True, verbose_name='active')
    is_occupied = models.BooleanField(editable=False, verbose_name='occupied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.theater.name + ": " + self.name
        if self.movie is not None:
            name = name + ": " + self.movie.name
        return name

    def clean(self):
        if hasattr(self, 'theater') and self.theater is not None and self.theater.is_active == False:
            raise ValidationError('The theater is not active.')
        if hasattr(self, 'movie') and self.movie is not None and self.movie.is_active == False:
            raise ValidationError('The movie is not active.')

    def get_total_seats_available(self):
        return Ticket.objects.filter(screen=self.id, customer__isnull=True).count()

class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = PhoneNumberField(null=True, blank=True, unique=True, default=None)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True, verbose_name='active')
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    class Meta:
      unique_together = ('screen', 'seat_number')

    id = models.AutoField(primary_key=True, verbose_name='number')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT, null=True, blank=True)
    seat_number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = MoneyField(decimal_places=2, default_currency='GBP', max_digits=4, editable=False)
    issued_at = models.DateTimeField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.screen.theater.name + ": " + self.screen.name + ": seat number " + str(self.seat_number)
        if self.customer is not None:
            name = name + ": " + self.customer.name
        return name

    def clean(self):
        if hasattr(self, 'screen') and self.screen.theater.is_active == False:
            raise ValidationError('Can not issue a ticket for inactive theater.')
        if hasattr(self, 'screen') and self.screen.movie is None:
            raise ValidationError('Can not issue a ticket without adding a movie to the screen first.')
        if hasattr(self, 'screen') and self.screen.is_active == False:
            raise ValidationError('Can not issue a ticket for inactive screen.')
        if hasattr(self, 'screen') and self.seat_number is not None and self.seat_number > self.screen.total_seats:
            raise ValidationError('The seat number "' + str(self.seat_number) + '" is higher than the total nubber of seats "' + str(self.screen.total_seats) + '".')
        if hasattr(self, 'customer') and self.customer is not None and self.customer.is_active == False:
            raise ValidationError('The customer is not active.')


