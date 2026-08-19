from django.urls import path

from .views import QuizViewSet

quiz_sets = QuizViewSet.as_view({'get': 'quiz_sets'})
quiz_detail = QuizViewSet.as_view({'get': 'detail'})
attempts = QuizViewSet.as_view({'get': 'attempts'})
mulai = QuizViewSet.as_view({'post': 'mulai'})
submit = QuizViewSet.as_view({'patch': 'submit'})
leaderboard = QuizViewSet.as_view({'get': 'leaderboard'})

urlpatterns = [
	path('', quiz_sets, name='mathquiz-list'),
	path('<int:pk>/', quiz_detail, name='mathquiz-detail'),
	path('mulai/', mulai, name='mathquiz-mulai'),
	path('attempts/', attempts, name='mathquiz-attempts'),
	path('<int:pk>/submit/', submit, name='mathquiz-submit'),
	path('leaderboard/', leaderboard, name='mathquiz-leaderboard'),
]