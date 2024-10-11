from django import forms
from facility.models import Facilities, Availability

class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facilities
        fields = ['name', 'description', 'image']  
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}), 
        }

class RestrictionForm(forms.Form):
    date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Fecha de restricción'
    )
    time_slot = forms.ChoiceField(
        label='Selecciona un horario para restringir',
        required=True
    )

    def __init__(self, *args, **kwargs):
        facility_id = kwargs.pop('facility_id', None)
        date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)

        if facility_id and date:
            # Mostrar solo los timeslots disponibles en la base de datos para esa fecha y facility
            available_timeslots = Availability.objects.filter(facilities_id=facility_id, date=date).order_by('time_slot')
            self.fields['time_slot'].choices = [(slot.id, slot.time_slot.strftime('%H:%M')) for slot in available_timeslots]