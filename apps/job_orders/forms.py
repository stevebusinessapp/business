from django import forms
from .models import JobOrder, JobOrderComment, JobOrderLayout

class JobOrderLayoutForm(forms.ModelForm):
    class Meta:
        model = JobOrderLayout
        fields = ['name', 'structure']

class JobOrderForm(forms.ModelForm):
    def __init__(self, *args, layout=None, **kwargs):
        super().__init__(*args, **kwargs)
        if layout is not None:
            # Dynamically add fields based on layout.structure (list of dicts)
            for col in layout.structure:
                field_name = col.get('name')
                label = col.get('label', field_name)
                field_type = col.get('type', 'char')
                required = col.get('required', False)
                if field_type == 'char':
                    self.fields[field_name] = forms.CharField(label=label, required=required)
                elif field_type == 'int':
                    self.fields[field_name] = forms.IntegerField(label=label, required=required)
                elif field_type == 'decimal':
                    self.fields[field_name] = forms.DecimalField(label=label, required=required)
                elif field_type == 'date':
                    self.fields[field_name] = forms.DateField(label=label, required=required, widget=forms.DateInput(attrs={'type': 'date'}))
                # Add more types as needed

    class Meta:
        model = JobOrder
        fields = ['title']

class JobOrderCommentForm(forms.ModelForm):
    class Meta:
        model = JobOrderComment
        fields = ['comment']
