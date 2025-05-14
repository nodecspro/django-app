from django.contrib import admin
from django.utils.html import (
    format_html,
)  # For rendering safe HTML in admin list display
from .models import MenuItem  # Import the model to be managed by this admin class


@admin.register(MenuItem)  # Decorator to register MenuItem with the admin site
class MenuItemAdmin(admin.ModelAdmin):
    """
    Custom admin interface configuration for the MenuItem model.
    Enhances usability and provides a more informative display in the Django admin.
    """

    # --- List Display Configuration ---
    # Specifies columns shown in the MenuItem change list page.
    list_display = (
        "name",  # The display name of the menu item.
        "menu_name",  # Identifier of the menu this item belongs to.
        "parent",  # String representation of the parent item (if any).
        "admin_resolved_url",  # Custom method to display the item's actual URL.
        "order",  # Sort order of the item.
    )

    # Adds filters to the sidebar of the change list page.
    # Allows filtering items by menu_name or parent.
    list_filter = ("menu_name", "parent")

    # Enables a search box for finding items by these fields.
    search_fields = ("name", "url", "named_url", "menu_name")

    # Default sort order for the change list.
    # Consistent with the model's Meta.ordering for predictability.
    ordering = ("menu_name", "parent__id", "order", "name")

    # --- Add/Change Form Configuration ---
    # Uses a text input with a lookup widget for the 'parent' ForeignKey.
    # Improves performance and UX when there are many MenuItem instances.
    raw_id_fields = ("parent",)

    # Organizes fields on the add/change form into logical sections (fieldsets).
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
                "classes": ("collapse",),  # Makes this section collapsible by default
                "fields": ("url", "named_url"),
                "description": "Set either Explicit URL (e.g., /about/) or Named URL (e.g., 'app:view'). Named URL is prioritized if valid.",
            },
        ),
        ("Display", {"fields": ("order",)}),  # Section for display-related properties
    )

    # --- Custom List Display Methods ---
    @admin.display(
        description="Resolved URL", ordering="named_url"
    )  # Allows sorting by the 'named_url' field
    def admin_resolved_url(self, obj: MenuItem) -> str:
        """
        Displays the item's resolved URL as a clickable link in `list_display`.
        Uses the model's `get_resolved_url` method.
        """
        url = obj.get_resolved_url()
        if url and url != "#":
            # format_html ensures that the HTML is properly escaped and safe.
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
                url,
                url,
            )
        return "—"  # Em dash for a more visually distinct placeholder if no URL
