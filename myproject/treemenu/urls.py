from django.urls import path
from django.views.generic import TemplateView

page_view = TemplateView.as_view(template_name="treemenu/page_example.html")

urlpatterns = [
    path("", page_view, name="treemenu_home"),
    path("about/", page_view, name="treemenu_about"),
    path("services/", page_view, name="treemenu_services"),
    path("services/web/", page_view, name="treemenu_services_web"),
    path("services/mobile/", page_view, name="treemenu_services_mobile"),
    path("contact/", page_view, name="treemenu_contact"),
    path("profile/", page_view, name="treemenu_profile"),
    path("settings/", page_view, name="treemenu_settings"),
    path("settings/account/", page_view, name="treemenu_settings_account"),
]
