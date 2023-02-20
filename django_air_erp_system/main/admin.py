from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(FlightModel)
admin.site.register(PriceModel)
admin.site.register(AirplaneModel)
admin.site.register(SeatModel)
admin.site.register(SeatTypeModel)
admin.site.register(TicketModel)
admin.site.register(PassengerModel)
admin.site.register(OptionModel)
admin.site.register(LuggageModel)