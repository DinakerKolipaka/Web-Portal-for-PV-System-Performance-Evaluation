from django.conf.urls import url
from SystemOwner import views

app_name = 'SystemOwner' #name = 'details' will be used along with app_name in views

urlpatterns = [
    url(r'^Details/$',views.OwnerView,name='Owner'),
    url(r'^EE/(?P<system_id>[0-9]+)/$',views.EE,name='EE'),
    url(r'^PE/(?P<system_id>[0-9]+)/$',views.PE,name='PE'),
    url(r'^Details/(?P<system_id>[0-9]+)/$',views.Details,name='Details'),
    url(r'^insert/$',views.InsertView,name='InsertView'),
    url(r'^EditView/$',views.EditView,name='EditView'),
    url(r'^EditProfile/$',views.EditProfile,name='EditProfile'),
    url(r'^insertPV/$',views.InsertPVView,name='InsertPVView'),
    url(r'^UploadXML/$',views.UploadXML,name='UploadXML'),
    url(r'^UploadXMLtoDB/$',views.UploadXMLtoDB,name='UploadXMLtoDB'),
    url(r'^DownloadResults(?P<system_id>[0-9]+)/$',views.DownloadResults,name='DownloadResults'),
    url(r'^CalculateEE/$',views.CalculateEE,name='CalculateEE'),
    url(r'^CompareResults/(?P<system_id>[0-9]+)/$',views.CompareResults,name='CompareResults'),
    url(r'^Logout/$',views.Logout,name='Logout'),
    url(r'^Delete/$',views.Delete,name='Delete'),
    url(r'^Update/$',views.Update,name='Update'),
    url(r'^UpdateAttempt/(?P<system_id>[0-9]+)/$',views.UpdateAttempt,name='UpdateAttempt'),
    url(r'^UpdateSystem/$',views.UpdateSystem,name='UpdateSystem'),
    url(r'^DeleteAttempt/(?P<system_id>[0-9]+)/$',views.DeleteAttempt,name='DeleteAttempt'),
    url(r'^GetLocation/$',views.getLocation,name='getLocation'),
    url(r'^ProvideAccess/$',views.ProvideAccess,name='ProvideAccess')
]
