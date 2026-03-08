from rest_framework.renderers import BrowsableAPIRenderer


class WilayahBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        context["page_title"] = renderer_context.get("page_title", "")
        return context
