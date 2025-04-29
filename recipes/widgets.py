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
        if isinstance(value, timedelta):
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes = remainder // 60
            return [hours, minutes]
        elif isinstance(value, str):
            # Manejo de strings tipo 'HH:MM:SS'
            try:
                h, m, *_ = map(int, value.split(':'))
                return [h, m]
            except:
                return [None, None]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if isinstance(values, list) and len(values) == 2 and all(values):
            try:
                hours = int(values[0])
                minutes = int(values[1])
                return timedelta(hours=hours, minutes=minutes)
            except ValueError:
                return None
        return None
    

