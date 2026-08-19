from django.urls import path

from .views import RamaAspirasiViewSet

form = RamaAspirasiViewSet.as_view({'get': 'form'})
submit = RamaAspirasiViewSet.as_view({'post': 'submit'})
hasil = RamaAspirasiViewSet.as_view({'get': 'hasil'})

urlpatterns = [
	path('', form, name='rama-form'),
	path('submit/', submit, name='rama-submit'),
	path('hasil/', hasil, name='rama-hasil'),
]