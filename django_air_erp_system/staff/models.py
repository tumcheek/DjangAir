from django.db import models
from main.models import TicketModel


# Create your models here.
class BoardingRegistrationModel(models.Model):
    ticket = models.OneToOneField(TicketModel, on_delete=models.CASCADE, related_name='board_registration')