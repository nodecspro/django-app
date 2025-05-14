from django.contrib import admin
from .models import MenuItem
from django.utils.html import format_html  # For safe HTML in admin display


@admin.register(
    MenuItem
)  # Registers MenuItem with the admin site using this custom class
class MenuItemAdmin(admin.ModelAdmin):
    # Columns to display in the MenuItem list view
    list_display = (
        "name",
        "menu_name",
        "parent",
        "admin_resolved_url",  # Custom display for the item's URL
        "order",
    )
    # Enables filtering by these fields in the list view's sidebar
    list_filter = ("menu_name", "parent")
    # Enables search functionality across these fields
    search_fields = ("name", "url", "named_url", "menu_name")
    # Improves UX for 'parent' ForeignKey selection, especially with many items
    raw_id_fields = ("parent",)
    # Default sorting for the list view
    ordering = ("menu_name", "parent__id", "order", "name")

    # Defines the layout of fields on the add/change form
    fieldsets = (
        (
            None,
            {  # Main section for core item properties
                "fields": ("name", "menu_name", "parent")
            },
        ),
        (
            "Link Target (choose one)",
            {  # Section for URL configuration
                "classes": ("collapse",),  # Makes this section collapsible
                "fields": ("url", "named_url"),
                "description": "Use Explicit URL (e.g., /contact/) or Named URL (e.g., 'app:view_name'). Named URL is prioritized.",
            },
        ),
        ("Display", {"fields": ("order",)}),  # Section for display-related properties
    )

    @admin.display(description="Resolved URL", ordering="named_url")
    def admin_resolved_url(self, obj: MenuItem):
        # Displays the item's resolved URL as a clickable link in the list_display.
        url = obj.get_resolved_url()
        if url and url != "#":
            # Use format_html for safe HTML rendering
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "-"  # Placeholder if no valid URL
