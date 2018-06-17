from django import forms
import datetime

class ListaAparicionForm(forms.Form):
    BUSQUEDA_CHOICES = (
        ('texto','Texto Tweet'),
        ('user_nombre', 'Nombre Usuario'),
        ('retweets', 'Retweets'),
        ('user_id', 'Id Usuario'),
    )
    tipo_busqueda = forms.ChoiceField(choices=BUSQUEDA_CHOICES)
    numero_resultados = forms.IntegerField(min_value=1, max_value=20)
    fecha_inicio = forms.DateField(input_formats=['%d/%m/%Y'], initial=datetime.date.today)
    fecha_final = forms.DateField(input_formats=['%d/%m/%Y'], initial=datetime.date.today)

class SubirArchivoForm(forms.Form):
    nombre_medio = forms.CharField(max_length=100)
    archivo_json = forms.FileField()

class BuscarMedioForm(forms.Form):
    nombre_medio = forms.CharField(max_length=100)

class FiltrarFechaForm(forms.Form):
    fecha_inicial = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, datetime.datetime.now().year+1)))
    fecha_final = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, datetime.datetime.now().year+1)))