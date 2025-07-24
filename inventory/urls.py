from django.urls import path
from . import views

urlpatterns = [
    # Auth & Redirect
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.dashboard_redirect, name='dashboard_redirect'),

    # Dashboards
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),

    # Inventory Management
    path('manage_inventory/', views.manage_inventory, name='manage_inventory'),
    path('add-item/', views.add_item, name='add_item'),
    path('manage-inventory/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('manage-inventory/delete/<int:item_id>/', views.delete_item, name='delete_item'),

    # Request Management
    path('manage_requests/', views.manage_requests, name='manage_requests'),
    path('request-item/', views.request_item, name='request_item'),
    path('requests/approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('requests/reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('request-report/<int:request_id>/', views.print_request_report, name='print_request_report'),

    # Users
    path('manage-users/', views.manage_users, name='manage_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/change-password/', views.change_user_password, name='change_user_password'),

    # Reports
    path('generate-report/', views.generate_reports, name='generate_report'),
    path('item-report/pdf/<int:item_id>/', views.export_item_report_pdf, name='export_item_report_pdf'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-all/', views.mark_all_as_read, name='mark_all_as_read'),
    path('notifications/acknowledge/<int:notif_id>/', views.acknowledge_notification, name='acknowledge_notification'),
]
