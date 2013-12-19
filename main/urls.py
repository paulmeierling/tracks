from django.conf.urls import patterns, include, url
from main import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    #user functionallity
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.user_login, name='user_login'),
    url(r'^logout$', views.user_logout, name='user_logout'),
    
    #dataset parts
    url(r'^(?P<dataset_id>\d+)$', views.dataset_overview, name='dataset_overview'),
    url(r'^(?P<dataset_id>\d+)/table$', views.table, name = 'table'),
    url(r'^(?P<dataset_id>\d+)\.json$', views.return_json, name='return_json'),
    
    #share parts
    url(r'^(?P<dataset_id>\d+)/share$', views.share, name='share'),
    url(r'^(?P<dataset_id>\d+)/remove_viewer$', views.remove_viewer, name='remove_viewer'),
    url(r'^(?P<dataset_id>\d+)/suggest_user$', views.suggest_user, name='suggest_user'),

    #Graph
    url(r'^graph$', views.graph, name='graph'),
    
    #datset modify functionallity
    url(r'^add_dataset$', views.add_dataset, name='add_dataset'),
    url(r'^(?P<dataset_id>\d+)/update_dataset$', views.update_dataset, name='update_dataset'),
    url(r'^(?P<dataset_id>\d+)/delete_dataset$', views.delete_dataset, name='delete_dataset'),
    

)