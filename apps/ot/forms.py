from django.forms import ModelForm
from .models.user import Freshman


class TSizeForm(ModelForm):
    class Meta:
        model = Freshman
        fields = ("tsize",)

    def __init__(self, *args, **kwargs):
        super(TSizeForm, self).__init__(*args, **kwargs)
        self.fields['tsize'].widget.attrs.update({'class': 'form-control'})
