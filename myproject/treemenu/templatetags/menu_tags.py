from typing import (
    List,
    Dict,
    Tuple,
    Set,
    Optional,
    Any,
)  # For comprehensive type hinting
from django import template
from django.db.models import QuerySet
from django.http import HttpRequest

from ..models import MenuItem  # Relative import for the MenuItem model

register = template.Library()  # Required for custom template tags

# Type alias for clarity
MenuItemProcessed = (
    MenuItem  # Could be a dataclass/TypedDict if not augmenting model instance
)
ItemsByIdMap = Dict[int, MenuItemProcessed]


def _get_menu_items_from_db(menu_name: str) -> QuerySet[MenuItem]:
    """Fetches and orders all items for a specific menu from DB."""
    # Ordering by parent_id, order, name is crucial for efficient tree construction
    # and predictable display order within levels.
    return MenuItem.objects.filter(menu_name=menu_name).order_by(
        "parent_id", "order", "name"
    )


def _process_menu_items(
    menu_items_qs: QuerySet[MenuItem], current_path: str
) -> Tuple[List[MenuItemProcessed], Optional[MenuItemProcessed], ItemsByIdMap]:
    """
    Prepares raw menu items: resolves URLs, finds active item, and indexes by ID.
    Augments model instances with 'resolved_url' and 'children_nodes' attributes.
    The database query is executed upon iterating `menu_items_qs`.
    """
    all_items_processed: List[MenuItemProcessed] = []
    active_item: Optional[MenuItemProcessed] = None
    items_by_id: ItemsByIdMap = {}

    for item in menu_items_qs:  # item is of type MenuItem
        # Resolve URL, prioritizing named_url. Fallback to explicit_url, then to '#'.
        # This logic could also live on the MenuItem model (e.g., item.get_display_url()).
        # Here, we add it dynamically to avoid modifying the model instance permanently if not desired,
        # or if the model's get_resolved_url has slightly different semantics for this context.
        item.resolved_url = (
            item.get_resolved_url()
        )  # Assuming model has get_resolved_url method

        # Identify active item by comparing its resolved URL with the current request path.
        if item.resolved_url == current_path:
            active_item = item

        item.children_nodes = []  # Initialize for storing child items
        items_by_id[item.id] = item
        all_items_processed.append(item)

    return all_items_processed, active_item, items_by_id


def _build_menu_tree(
    all_items_processed: List[MenuItemProcessed], items_by_id: ItemsByIdMap
) -> List[MenuItemProcessed]:
    """
    Constructs the hierarchical tree structure from the flat list of processed items.
    Populates 'children_nodes' for each parent.
    """
    root_items: List[MenuItemProcessed] = []
    for item in all_items_processed:
        if item.parent_id and item.parent_id in items_by_id:
            parent = items_by_id[item.parent_id]
            parent.children_nodes.append(
                item
            )  # Children are pre-sorted by the initial DB query
        elif not item.parent_id:  # Item without a parent is a root item
            root_items.append(item)
    return root_items


def _determine_expanded_pks(
    active_item: Optional[MenuItemProcessed], items_by_id: ItemsByIdMap
) -> Set[int]:
    """
    Identifies PKs of items that should be expanded in the menu.
    Includes the active item and all its direct ancestors.
    """
    expanded_pks: Set[int] = set()
    if active_item:
        expanded_pks.add(active_item.pk)  # Active item's children should be visible

        # Traverse up the parent chain to expand all ancestors
        current_ancestor: Optional[MenuItemProcessed] = active_item
        while (
            current_ancestor
            and current_ancestor.parent_id
            and current_ancestor.parent_id in items_by_id
        ):
            # Check current_ancestor itself before accessing parent_id
            parent = items_by_id[current_ancestor.parent_id]
            expanded_pks.add(parent.pk)
            current_ancestor = parent  # Move to the next ancestor

    return expanded_pks


# --- Main Template Tag ---


@register.inclusion_tag("treemenu/menu_template.html", takes_context=True)
def draw_menu(context: Dict[str, Any], menu_name: str) -> Dict[str, Any]:
    """
    Renders a menu specified by 'menu_name'.
    Handles fetching, processing, tree building, and determining expanded state.
    The single database query occurs when `_process_menu_items` iterates the QuerySet.
    """
    request: Optional[HttpRequest] = context.get("request")

    # Default context values for the template tag
    tag_context: Dict[str, Any] = {
        "menu_nodes": [],
        "menu_name": menu_name,
        "active_item_pk": None,
        "expanded_pks": set(),
        "request": request,
    }

    if not request:
        # Consider logging this as it's crucial for active item highlighting.
        # logger.warning(f"Template tag 'draw_menu' for '{menu_name}': HttpRequest not found in context.")
        return tag_context

    current_path: str = request.path

    # Step 1: Fetch menu items (QuerySet is lazy, DB hit in Step 2)
    menu_items_qs: QuerySet[MenuItem] = _get_menu_items_from_db(menu_name)

    # Step 2: Process items - resolve URLs, find active, index by ID. DB query executes here.
    all_items_processed, active_item, items_by_id = _process_menu_items(
        menu_items_qs, current_path
    )

    if not all_items_processed:  # No items found for this menu_name
        return tag_context

    # Step 3: Build the hierarchical tree structure
    root_items: List[MenuItemProcessed] = _build_menu_tree(
        all_items_processed, items_by_id
    )

    # Step 4: Determine which items' children should be displayed (expanded)
    expanded_pks: Set[int] = _determine_expanded_pks(active_item, items_by_id)

    # Update the context for the inclusion template
    tag_context.update(
        {
            "menu_nodes": root_items,
            "active_item_pk": active_item.pk if active_item else None,
            "expanded_pks": expanded_pks,
        }
    )
    return tag_context
