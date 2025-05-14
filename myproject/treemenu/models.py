from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)  # Standard logger for this module


class MenuItem(models.Model):
    # --- Core Fields ---
    name = models.CharField(
        _("Display Name"), max_length=100, help_text=_("Visible name of the menu item.")
    )
    menu_name = (
        models.CharField(  # Groups items into a specific menu (e.g., 'main_menu')
            _("Menu Name"),
            max_length=50,
            db_index=True,  # Improves query performance when filtering by menu_name
            help_text=_("Identifier for the menu (e.g., 'main_menu', 'sidebar_menu')."),
        )
    )
    parent = models.ForeignKey(  # Self-referential FK for hierarchical structure
        "self",
        verbose_name=_("Parent Item"),
        null=True,
        blank=True,  # Root items have no parent
        related_name="children",  # Access children via item.children.all()
        on_delete=models.CASCADE,  # Deleting a parent deletes its children
        help_text=_("Select parent for sub-menu; leave blank for top-level."),
    )
    # --- URL Configuration ---
    url = models.CharField(  # For static, explicit URLs
        _("Explicit URL"),
        max_length=255,
        blank=True,
        help_text=_("Direct URL (e.g., /about/). Used if Named URL is blank or fails."),
    )
    named_url = models.CharField(  # For URLs resolved via Django's 'reverse()'
        _("Named URL"),
        max_length=100,
        blank=True,
        help_text=_("URL pattern name (e.g., 'app:view'). Takes precedence if valid."),
    )
    # --- Display & Ordering ---
    order = models.IntegerField(
        _("Order"),
        default=0,
        help_text=_("Sort order within the same parent/level (lower numbers first)."),
    )

    class Meta:
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        # Default ordering for queries and admin display.
        # `parent__id` assists in some scenarios, though tree building is explicit in the tag.
        ordering = ["menu_name", "parent__id", "order", "name"]

    def __str__(self):
        # Informative string representation for admin/debug.
        parent_status = (
            " (Root)" if not self.parent_id else f" (Parent ID: {self.parent_id})"
        )
        return f"'{self.name}' [{self.menu_name}]{parent_status}"

    def get_resolved_url(self):
        # Determines the item's actual URL, prioritizing named_url.
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                logger.warning(
                    f"MenuItem ID {self.pk}: Named URL '{self.named_url}' failed to resolve. Falling back to explicit URL."
                )
                return self.url or "#"  # Fallback to explicit or placeholder
        return self.url or "#"  # Use explicit URL or placeholder if no named_url

    def clean(self):
        # Custom model validation. Called by ModelForms (admin) and explicitly in save().
        super().clean()

        # Prevent circular parent-child relationships.
        if self.parent_id:
            ancestor = self.parent
            visited_pks = {
                self.parent_id
            }  # Track visited ancestors to detect pre-existing loops
            while ancestor:
                if ancestor.pk == self.pk:  # Cannot be its own (grand)parent
                    raise ValidationError(
                        {
                            "parent": _(
                                "Circular dependency: Item cannot be its own ancestor."
                            )
                        }
                    )
                if (
                    ancestor.parent_id in visited_pks
                ):  # Safety against pre-existing corrupted data
                    logger.error(
                        f"MenuItem ID {self.pk}: Loop detected in parent chain at parent ID {ancestor.parent_id} during validation."
                    )
                    break
                if ancestor.parent_id:  # Add only if there's a next parent to visit
                    visited_pks.add(ancestor.parent_id)
                ancestor = ancestor.parent

        # Ensure menu_name is provided.
        if not self.menu_name or not self.menu_name.strip():
            raise ValidationError({"menu_name": _("Menu Name is required.")})

    def save(self, *args, **kwargs):
        # Ensures all model validations (including clean()) run on every save.
        self.full_clean()
        super().save(*args, **kwargs)
