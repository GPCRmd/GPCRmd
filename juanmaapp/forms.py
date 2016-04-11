from django import forms

from .models import Formup

class PostForm(forms.ModelForm):

    class Meta:
        model = Formup
        fields = ('UNIPROTid', 'iso', 'MUT','Nam', 'ORGAN', 'DescMOL','NETc', 'INCHI', 'inchik', 'SMI', 'resnamMOL', 'numMOL', 'MAINprot','MAINlig', 'IONresn', 'IONnum', 'COMtyp', 'idproT', 'idcoM', 'Msour', 'PDB', 'desc', 'mTEMP', 'METH', 'SOFT', 'SOFTver', 'ffield', 'MEMB', 'Solv', 'PDBcoor', 'PSF', 'topPSF', 'par', 'DCD')

