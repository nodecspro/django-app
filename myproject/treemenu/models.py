from django.core.exceptions import ValidationError
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _
import logging
from typing import Optional  # For type hinting

logger = logging.getLogger(__name__)


class MenuItem(models.Model):
    """
    Represents an item in a hierarchical, named menu.
    Menus are rendered via a template tag and support dynamic expansion
    based on the current URL.
    """

    name = models.CharField(
        _("Display Name"), max_length=100, help_text=_("Visible name of the menu item.")
    )
    menu_name = models.CharField(
        _("Menu Name"),
        max_length=50,
        db_index=True,  # Essential for efficient querying of specific menus
        help_text=_("Identifier for the menu (e.g., 'main_menu', 'sidebar_menu')."),
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent Item"),
        null=True,
        blank=True,  # Allows for root (top-level) menu items
        related_name="children",  # Enables item.children.all()
        on_delete=models.CASCADE,  # Standard for hierarchical data integrity
        help_text=_("Select parent for sub-menu; leave blank for top-level."),
    )
    url = models.CharField(
        _("Explicit URL"),
        max_length=2048,  # Standard max URL length (RFC 2616)
        blank=True,
        help_text=_(
            "Direct URL (e.g., /about/). Used if Named URL is blank or fails to resolve."
        ),
    )
    named_url = models.CharField(
        _("Named URL"),
        max_length=100,  # Typically, named URLs are not excessively long
        blank=True,
        help_text=_(
            "URL pattern name (e.g., 'app_name:view_name'). Takes precedence if valid."
        ),
    )
    order = models.IntegerField(
        _("Order"),
        default=0,
        help_text=_(
            "Sort order within the same parent/level (lower numbers appear first)."
        ),
    )

    class Meta:
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        # Default ordering ensures consistent behavior in queries and admin.
        # `parent__id` helps to group items, though the tree is built explicitly by the templatetag.
        ordering = ["menu_name", "parent__id", "order", "name"]

    def __str__(self) -> str:
        parent_status = (
            " (Root)"
            if not self.parent_id
            else f" (Parent: {self.parent.name if self.parent else 'N/A'})"
        )
        return f"'{self.name}' [{self.menu_name}]{parent_status}"

    def get_resolved_url(self) -> str:
        """
        Determines the item's display URL, prioritizing named_url.
        Returns '#' as a fallback if no valid URL can be determined.
        """
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                logger.warning(
                    f"MenuItem (ID: {self.pk}, Name: '{self.name}'): "
                    f"Named URL '{self.named_url}' failed to resolve. Falling back."
                )
                # Fallback to explicit URL if named_url resolution fails
                return self.url or "#"
        # Use explicit URL if no named_url is provided
        return self.url or "#"

    def clean(self) -> None:
        """
        Performs model-level validation before saving.
        Ensures data integrity, e.g., preventing circular dependencies.
        """
        super().clean()

        # Prevent circular parent-child relationships.
        if self.parent_id:  # Only proceed if a parent is actually assigned
            # Check against self to prevent item being its own parent
            if self.parent_id == self.pk and self.pk is not None:
                raise ValidationError(
                    {"parent": _("An item cannot be its own parent.")}
                )

            # Traverse up the ancestor chain to detect cycles
            ancestor: Optional["MenuItem"] = self.parent
            visited_pks = {
                self.parent_id
            }  # Track visited ancestors to detect pre-existing loops

            while ancestor:
                if (
                    ancestor.pk == self.pk
                ):  # Current item found in its own ancestor chain
                    raise ValidationError(
                        {
                            "parent": _(
                                "Circular dependency: Item cannot be an ancestor of itself."
                            )
                        }
                    )
                # Check for loops in potentially corrupted existing data by tracking visited parent PKs
                if ancestor.parent_id and ancestor.parent_id in visited_pks:
                    logger.error(
                        f"MenuItem (ID: {self.pk}): Loop detected in parent chain via parent ID "
                        f"{ancestor.parent_id} during validation. Data might be corrupted."
                    )
                    # Optionally, raise an error here if strict data integrity is paramount
                    # raise ValidationError({'parent': _("Corrupted parent chain detected (loop).")})
                    break  # Stop traversal to prevent infinite loop
                if ancestor.parent_id:
                    visited_pks.add(ancestor.parent_id)
                ancestor = ancestor.parent

        # Ensure menu_name is provided and not just whitespace.
        if not self.menu_name or not self.menu_name.strip():
            raise ValidationError(
                {"menu_name": _("Menu Name is required and cannot be empty.")}
            )

    def save(self, *args, **kwargs) -> None:
        """
        Overrides the default save method to ensure full_clean() is called,
        enforcing all model validations even for programmatic saves.
        """
        self.full_clean()  # Calls field validation, model clean(), and unique constraint checks
        super().save(*args, **kwargs)
