from action_components import build_banner, build_buttons
from action_context import ActionContext


def render_page(request):
    context = ActionContext(storage_enabled=request.get("use_storage", False))
    components = {"bottom": {"buttons": build_buttons(context, request)}}
    banner = build_banner(context, request)
    if banner is not None:
        components["banner"] = banner
    return {
        "components": components,
        "action_storage": context.materialize(),
    }
