
class HTMXMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.htmx = request.headers.get('HX-Request')
        request.htmx_request = request.headers.get('HX-Request')
        request.htmx_boosted = request.headers.get('HX-Boosted')
        request.htmx_current_url = request.headers.get('HX-Current-URL')
        request.htmx_history_restore = request.headers.get('HX-History-Restore-Request')
        request.htmx_prompt = request.headers.get('HX-Prompt')
        request.htmx_target = request.headers.get('HX-Target')
        request.htmx_trigger_name = request.headers.get('HX-Trigger-Name')
        request.htmx_trigger_id = request.headers.get('HX-Trigger')
        response = self.get_response(request)
        return response

class Additionals:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # code after processing view (before template process)
        groups = request.user.groups
        admin_flag = "store_admin"

        request.is_admin = groups.filter(name=admin_flag).exists()
        response = self.get_response(request)
        # code after processing template (before send back to client)
        return response