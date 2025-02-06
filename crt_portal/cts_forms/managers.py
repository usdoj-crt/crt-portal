from django.db import models
from .model_variables import PROTECTED_MODEL_CHOICES


class ActiveProtectedClassChoiceManager(models.Manager):
    """
    Provide functionality to retrieve only instances
    which are currently defined in PROTECTED_MODEL_CHOICES
    and to be made available for selection in forms
    """

    @staticmethod
    def get_active_choices():
        return [
            choice[0]
            for choice
            in PROTECTED_MODEL_CHOICES
            if 'gender' not in choice[1]
        ]

    def get_queryset(self):
        return super().get_queryset().filter(value__in=self.get_active_choices())
