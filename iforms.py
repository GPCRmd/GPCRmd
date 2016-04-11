from django.forms import ModelForm
from .imodels import DyndbModel

# Create the form class.
class DyndbModelForm(ModelForm):
    class Meta:
        model = DyndbModel
        fields ='__all__' 

# Creating a form to add an article.
form = DyndbModelForm()

# Creating a form to change an existing article.
#dyndbmodel= DyndbModel.objects.get(pk=1)
#form = DyndbModelForm(instance=dyndbmodel)
