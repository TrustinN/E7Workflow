from src.app.frontend.events import EventIDProvider


class WKEvents:
    provider = EventIDProvider("WorkspaceEvents")

    WK_CREATED_ROOT = provider.genID()
    WK_CREATED = provider.genID()
    WK_UPDATED = provider.genID()
    WK_FOCUSED = provider.genID()
    WK_EXPORTED = provider.genID()
    WK_IMPORTED = provider.genID()
