from django.forms import ModelForm, TextInput, CharField, HiddenInput
from main.models import Friend, UserPreferences

class FriendForm(ModelForm):
    form_name = CharField(widget=HiddenInput, initial='Friend')
    class Meta:
        model = Friend
        fields = ['name', 'remind_period_days']
        widgets = {
            'name': TextInput,
        }
