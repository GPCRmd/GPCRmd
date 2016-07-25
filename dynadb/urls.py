from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.contrib import admin

from . import views

app_name= 'dynadb'
urlpatterns = [
    url(r'^prueba_varios/$', TemplateView.as_view(template_name='dynadb/pruebamult_template.html'), name="prueba_varios"),
#    url(r'^prueba_varios/$', views.profile_setting, name='PRUEBA_varios'),
    url(r'^profile_setting/$', views.profile_setting, name='profile_setting'),
    url(r'^sub_sim/$', views.sub_sim, name='sub_sim'),
    url(r'^name/$', views.get_name, name='name'),
    url(r'^dyndbfiles/$', views.get_DyndbFiles, name='dyndbfiles'),
    url(r'^pruebadyndbfiles/$', views.get_Prueba, name='pruebadyndbfiles'),
    url(r'^db_inputform/$', views.db_inputformMAIN, name='db_inputform'),
    url(r'^db_author_information/$', views.get_Author_Information, name='db_author_information'),
    url(r'^db_dynamics/$', views.get_Dynamics, name='db_dynamics'),
    url(r'^db_files/$', views.get_FilesCOMPLETE, name='db_files'),
    url(r'^db_protein/$', views.get_ProteinForm, name='db_protein'),
    url(r'^db_molecule/$', views.get_Molecule, name='db_molecule'),
    url(r'^db_component/$', views.get_Component, name='db_component'),
    url(r'^db_model/$', views.get_Model, name='db_model'),
    url(r'^db_compoundform/$', views.get_CompoundForm, name='db_compoundform'),
    url(r'^your_name/$', views.get_name, name='your_name'),
    url(r'^thanks/$', views.get_name, name='thanks'),
    url(r'^admin/', admin.site.urls),
    url(r'^protein/$', views.PROTEINview, name='protein'),
    url(r'^references/$', views.REFERENCEview, name='references'),
    url(r'^REFERENCEfilled/$', views.REFERENCEview, name='REFERENCEfilled'),
    url(r'^PROTEINfilled/$', views.PROTEINview, name='PROTEINfilled'),
    url(r'^molecule/$', views.SMALL_MOLECULEview, name='molecule'),
    url(r'^molecule2/$', views.SMALL_MOLECULEview2, name='molecule2'),
    url(r'^model/$', views.MODELview, name='model'),
    url(r'^dynamics/$', views.DYNAMICSview, name='dynamics'),
    url(r'^form/$', views.get_formup, name='form'),
    url(r'^submitted/$', views.SUBMITTEDview, name='submitted')
#    url(r'^some_temp/$', views.some_view, name='some_temp')

]
