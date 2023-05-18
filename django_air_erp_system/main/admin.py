from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.FlightModel)
admin.site.register(models.PriceModel)
admin.site.register(models.AirplaneModel)
admin.site.register(models.SeatModel)
admin.site.register(models.SeatTypeModel)
admin.site.register(models.TicketModel)
admin.site.register(models.OptionModel)
admin.site.register(models.LuggageModel)
admin.site.register(models.EmailSubjectModel)
