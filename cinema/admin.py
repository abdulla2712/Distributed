from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

# Register your models here.

from .models import User, Theater, Screen, Category, Movie, Ticket, Customer

class CustomUserAdmin(UserAdmin):
    fieldsets=(
      *UserAdmin.fieldsets,
      (
        'Additional Info',
        {
          'fields':(
            'phone',
            'salary',
          )
        }
      )
    )

class ScreenAdmin(admin.ModelAdmin):
    readonly_fields = ["is_occupied"]

    def save_model(self, request, obj, form, change):
        if obj.movie is not None:
            now = timezone.now()
            if now >= obj.movie.starts_at and now <= obj.movie.ends_at:
                obj.is_occupied = True
            else:
                obj.is_occupied = False
        else:
            Ticket.objects.all().filter(screen=obj.id).delete()
            obj.is_occupied = False

        super().save_model(request, obj, form, change)

        if obj.movie is not None:
            ticker_count = Ticket.objects.all().filter(screen=obj.id).count()
            if ticker_count == 0:
                price = 10
                if obj.type == Screen.VIP:
                    price = 45
                tickets = []
                for i in range(1, obj.total_seats + 1):
                    tickets.append(Ticket(screen=obj, seat_number=i, price=price))
                Ticket.objects.bulk_create(tickets)


class MovieAdmin(admin.ModelAdmin):
    readonly_fields = ["is_active", "created_by"]

    def save_model(self, request, obj, form, change):
        if timezone.now() > obj.ends_at:
            obj.is_active = False
        else:
            obj.is_active = True

        obj.created_by = request.user
        super().save_model(request, obj, form, change)

class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by"]

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ["price", "issued_at"]

    def save_model(self, request, obj, form, change):
      if obj.screen.type == Screen.VIP:
        obj.price = 45
      else:
        obj.price = 10

      if obj.customer is None:
        obj.issued_at = None
      else:
        if obj.issued_at is None:
            obj.issued_at = timezone.now()

      super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Theater)
admin.site.register(Screen, ScreenAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Category)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Ticket, TicketAdmin)
