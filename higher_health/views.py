from django.http import JsonResponse

class HealthcheckView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        status = 200
        resp = {"up": True}
        return JsonResponse(resp, status=status)
