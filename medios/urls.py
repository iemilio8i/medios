from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import views

app_name = 'medios'
urlpatterns = [
    path('subir-archivo/', views.subir_archivo, name='subir_archivo_sin'),
    path('subir-archivo/<slug:medio_nombre>/', views.subir_archivo, name='subir_archivo'),

    # Test
    path('form/', TemplateView.as_view(template_name='app/form.html'), name='form'),
    path('medio-index/', views.control_flow_medio_index, name='medio_index'),
    # TODO Todavía por definir el id del medio (MongoDB)
    path('medio-index/<slug:medio_nombre>/', views.control_flow_medio_index, name='medio_index'),
    path('lista-medios', views.lista_medios, name='lista_medios'),

    # Plots
    path('bokeh/', views.index, name='bokeh_test'),
    path('bokeh-tweets/', views.bokeh_prueba_tweet, name='tweet_bokeh'),
    path('grafica-palabra/', views.grafica_palabras_form, name='grafica_palabra'),

]