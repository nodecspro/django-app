from django import template
from django.urls import reverse, NoReverseMatch
from ..models import MenuItem  # Relative import for the MenuItem model

register = template.Library()  # Required for custom template tags

# --- Helper Functions for draw_menu ---


def _get_menu_items_from_db(menu_name: str):
    # Fetches and orders all items for a specific menu from DB.
    # Ordering by parent_id, order, name is crucial for tree construction and display.
    return MenuItem.objects.filter(menu_name=menu_name).order_by(
        "parent_id", "order", "name"
    )


def _process_menu_items(menu_items_qs, current_path: str):
    # Prepares raw menu items: resolves URLs, finds active item, and indexes by ID.
    # Augments model instances with 'resolved_url' and 'children_nodes'.
    # Database query is executed here upon iteration of menu_items_qs.
    all_items_processed = []
    active_item = None
    items_by_id = (
        {}
    )  # For quick lookup by ID during tree building and ancestor traversal

    for item_model in menu_items_qs:
        # Resolve URL: prioritizes named_url, falls back to url, then to "#"
        if item_model.named_url:
            try:
                item_model.resolved_url = reverse(item_model.named_url)
            except NoReverseMatch:
                item_model.resolved_url = item_model.url or "#"
        else:
            item_model.resolved_url = item_model.url or "#"

        # Identify active item by comparing its resolved URL with the current request path
        if item_model.resolved_url == current_path:
            active_item = item_model

        item_model.children_nodes = []  # Initialize for storing child items
        items_by_id[item_model.id] = item_model
        all_items_processed.append(item_model)

    return all_items_processed, active_item, items_by_id


def _build_menu_tree(all_items_processed, items_by_id):
    # Constructs the hierarchical tree structure from the flat list of processed items.
    # Populates 'children_nodes' for each parent.
    root_items = []  # Top-level menu items
    for item in all_items_processed:
        if item.parent_id and item.parent_id in items_by_id:
            parent = items_by_id[item.parent_id]
            parent.children_nodes.append(
                item
            )  # Children are already sorted due to initial query order
        elif not item.parent_id:  # Item without a parent is a root item
            root_items.append(item)
    return root_items


def _determine_expanded_pks(active_item, items_by_id):
    # Identifies primary keys of items that should be expanded in the menu.
    # Includes the active item itself and all its direct ancestors.
    expanded_pks = set()
    if active_item:
        expanded_pks.add(active_item.pk)  # Active item's children should be visible
        current_ancestor = active_item
        # Traverse up the parent chain to expand all ancestors
        while current_ancestor.parent_id and current_ancestor.parent_id in items_by_id:
            parent = items_by_id[current_ancestor.parent_id]
            expanded_pks.add(parent.pk)
            current_ancestor = parent
    return expanded_pks


# --- Main Template Tag ---


@register.inclusion_tag("treemenu/menu_template.html", takes_context=True)
def draw_menu(context, menu_name: str):
    # Renders a menu specified by 'menu_name'.
    # Handles fetching, processing, tree building, and determining expanded state.
    # Passes context to 'treemenu/menu_template.html'.
    request = context.get("request")  # Essential for determining the current path

    # Default context for the template tag if data is missing or request is unavailable
    empty_context_for_tag = {
        "menu_nodes": [],
        "menu_name": menu_name,
        "active_item_pk": None,
        "expanded_pks": set(),
        "request": request,
    }

    if not request:
        # Log or handle missing request object if necessary for debugging
        # logger.warning(f"Request object not found in context for draw_menu '{menu_name}'.")
        return empty_context_for_tag

    current_path = request.path

    # Step 1: Fetch menu items (single DB query happens in _process_menu_items)
    menu_items_qs = _get_menu_items_from_db(menu_name)

    # Step 2: Process items - resolve URLs, find active, index by ID
    all_items_processed, active_item, items_by_id = _process_menu_items(
        menu_items_qs, current_path
    )

    if not all_items_processed:  # No items found for this menu_name
        return empty_context_for_tag

    # Step 3: Build the hierarchical tree structure
    root_items = _build_menu_tree(all_items_processed, items_by_id)

    # Step 4: Determine which items' children should be displayed (expanded)
    expanded_pks = _determine_expanded_pks(active_item, items_by_id)

    # Prepare context for the inclusion template
    return {
        "menu_nodes": root_items,  # List of top-level MenuItem objects
        "active_item_pk": active_item.pk if active_item else None,
        "expanded_pks": expanded_pks,  # Set of PKs of items to be expanded
        "menu_name": menu_name,  # Name of the rendered menu
        "request": request,  # Pass request for potential use in sub-templates
    }
