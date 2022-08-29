from django.forms import ModelForm, TextInput, CharField, HiddenInput, DateInput
from main.models import Friend, UserPreferences

class Html5DateInput(DateInput):
    input_type = 'date'

class FriendCreateForm(ModelForm):
    form_name = CharField(widget=HiddenInput, initial='Friend')
    class Meta:
        model = Friend
        fields = ['name', 'remind_period_days']
        widgets = {
            'name': TextInput,
        }

class FriendEditForm(ModelForm):
    class Meta:
        model = Friend
        fields = ['log', 'next_reminder']
        widgets = {
            'next_reminder': Html5DateInput
        }
