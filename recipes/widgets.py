from django import forms
from django.forms.widgets import NumberInput
from datetime import timedelta

class RecipeDurationWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            NumberInput(attrs={'placeholder': 'HH', 'style': 'width: 50px;', 'min': '0', 'max': '99'}),
            NumberInput(attrs={'placeholder': 'MM', 'style': 'width: 50px;', 'min': '0', 'max': '59'}),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            hours, remainder = divmod(value.total_seconds(), 3600)
            minutes = remainder // 60
            return [int(hours), int(minutes)]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if all(values):
            try:
                hours = int(values[0])
                minutes = int(values[1])
                return timedelta(hours=hours, minutes=minutes)
            except ValueError:
                return None
        return None