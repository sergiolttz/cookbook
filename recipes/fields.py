from django import forms
from datetime import timedelta

class TimeDeltaField(forms.DurationField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, timedelta):
            return value
        try:
            hours, minutes, seconds = map(int, value.split(':'))
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except ValueError:
            raise forms.ValidationError(self.error_messages['invalid'], code='invalid')

    def prepare_value(self, value):
        if isinstance(value, timedelta):
            hours, remainder = divmod(value.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        return super().prepare_value(value)