from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import views

app_name = 'medios'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', login_required(views.ResultsView.as_view()), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),

    # Test
    path('form/', TemplateView.as_view(template_name='app/form.html'), name='form'),
    path('medio-index/', views.medio_index, name='medio_index'),
    # TODO Todavía por definir el id del medio (MongoDB)
    path('medio-index/<slug:medio_id>/', views.medio_index, name='medio_index'),

    # Tweets
    path('tweets/<slug:tweet_id>/', views.detail_tweet, name='tweet_detail'),
    path('tweet_list/', views.list_tweets, name='tweet_index'),

    # Plots
    path('bokeh/', views.index, name='bokeh_test'),
    path('bokeh-tweets/', views.bokeh_prueba_tweet, name='tweet_bokeh'),
    path('grafica-palabra/', views.grafica_palabras_form, name='grafica_palabra'),

]