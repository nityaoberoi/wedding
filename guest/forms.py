from django import forms

from guest.models import Guest, COMING_OPTS

class GuestForm(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True, label="Email:")
    name = forms.CharField(max_length=100, required=False, label="Name:")
    coming = forms.ChoiceField(required=False, label="Will you be joining us in Pune?", choices=COMING_OPTS)
    count = forms.IntegerField(required=False, label="Number attending:")
    checkin = forms.DateField(required=False, label="Checking in at Bonboutique? If so, when?")
    checkout = forms.DateField(required=False, label="...and checking out?")    
    ride_from_bom = forms.BooleanField(required=False, label="Need a ride from BOM on Jun 9th?")
    
    class Meta:
        model = Guest
        exclude = ('message', 'updated')
    
    def clean_message(self):
        message = forms.cleaned_data['message']
    # def clean_coming(self):
    #        coming = forms.cleaned_data['coming']
    #        for v, k in COMING_OPTS:
    #            if v == val:
    #                return k
    #    return 'Yes'
        
class GuestEmailForm(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True, label="Email:")
    
    class Meta:
        model = Guest
        fields = ('email', )