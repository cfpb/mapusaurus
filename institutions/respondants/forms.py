from django import forms

class InstitutionSearchForm(forms.Form):
    name_contains = forms.CharField(max_length=40)
