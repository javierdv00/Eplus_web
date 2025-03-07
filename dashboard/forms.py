from django import forms

class UploadFileForm(forms.Form):
    project_name = forms.CharField(label="Project Name", max_length=255)
    file = forms.FileField()
