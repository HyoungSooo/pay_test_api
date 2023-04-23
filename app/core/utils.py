from rest_framework.response import Response


def create_response_msg(code, msg, data=None):
    return Response(
        {
            "meta": {
                "code": code,
                "message": msg,
            },

            "data": data
        }, status=code
    )
