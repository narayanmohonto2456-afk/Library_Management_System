from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Books CRUD
    path('books/',              views.book_list,   name='book_list'),
    path('books/add/',          views.book_add,    name='book_add'),
    path('books/<int:pk>/',     views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/',views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Members CRUD
    path('members/',                  views.member_list,   name='member_list'),
    path('members/add/',              views.member_add,    name='member_add'),
    path('members/<int:pk>/',         views.member_detail, name='member_detail'),
    path('members/<int:pk>/edit/',    views.member_update, name='member_update'),
    path('members/<int:pk>/delete/',  views.member_delete, name='member_delete'),

    # Transactions
    path('issue/',                         views.issue_book,    name='issue_book'),
    path('issued/',                        views.issued_books,  name='issued_books'),
    path('return/<int:record_id>/',        views.return_book,   name='return_book'),

    # Reports
    path('reports/overdue/',  views.overdue_report, name='overdue_report'),
    path('reports/history/',  views.borrow_history, name='borrow_history'),
]
