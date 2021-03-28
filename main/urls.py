from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import (
    LedgerListView,
    LedgerUpdateView,
    LedgerDetailView,
    # LedgerCreateView,
    PersonListView,
    ItemListView,
    ItemUpdateView,
    ItemDetailView,
    ItemCreateView,
    PersonDetailView,
    ledger_create,
    LedgerListJson,
    ItemListJson,
    PersonListJson,
    OrderListJson,
    PersonUpdateView,
    OrderUpdateView,
    export_csv_items,
    export_csv_ledgers,
    export_csv_persons,
    export_csv_person_ledger,
    OrderItemCreateView
    # ImageModalTemplateView
)

app_name='main'

urlpatterns=[
    path('foo/', TemplateView.as_view(template_name='main/base2.html')),
    path('foo2/', TemplateView.as_view(template_name='main/foo2.html')),
    path("table/", TemplateView.as_view(template_name='main/table.html'), name="table"),

    path("i/<int:pk>", ItemDetailView.as_view(), name="item_detail"),
    path("i/<int:pk>/update", ItemUpdateView.as_view(), name="item_update"),
    path("i/create/", ItemCreateView.as_view(), name="item_create"),
    path("i/", ItemListView.as_view(), name="item_list"),
    path("i/msg/<str:msg>", ItemListView.as_view(), name="item_list"),
    path("i/data", ItemListJson.as_view(), name="item_list_json"),

    path("u/<int:pk>", PersonDetailView.as_view(), name="person_detail"),
    path("u/", PersonListView.as_view(), name="person_list"),
    path("u/data/", PersonListJson.as_view(), name="person_list_json"),
    path("u/<int:pk>/update", PersonUpdateView.as_view(), name="person_update"),

    path("login/", auth_views.LoginView.as_view(template_name='main/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name='main/login.html'), name="logout"),

    path("", LedgerListView.as_view(),name='homepage'),
    path("l/msg/<str:msg>", LedgerListView.as_view(),name='homepage'),
    path('l/data/', LedgerListJson.as_view(), name='ledger_list_json'),
    path("l/<int:pk>/data", OrderListJson.as_view(), name="order_list_json"),
    path("l/<int:pk>", LedgerDetailView.as_view(), name="ledger_detail"),
    path("l/<int:pk>/update", LedgerUpdateView.as_view(), name="ledger_update"),
    path("o/<int:pk>/update", OrderUpdateView.as_view(), name="ledger_order_update"),# l/<int:pk>/
    path("l/create", ledger_create, name="ledger_create"),
    path("o/update/<int:pk>", OrderItemCreateView.as_view(), name="order_item_create"),

    path("export-csv-items", export_csv_items, name="export_csv_items"),
    path("export-csv-ledgers", export_csv_ledgers, name="export_csv_ledgers"),
    path("export-csv-persons", export_csv_persons, name="export_csv_persons"),
    path("export-csv-person-ledger/<int:pk>", export_csv_person_ledger, name="export_csv_person_ledger"),

    # path("i/<int:pk>/img", ImageModalTemplateView.as_view(), name="image_modal")
]