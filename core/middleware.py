# from rest_framework_simplejwt.authentication import JWTAuthentication
# from django.utils.deprecation import MiddlewareMixin
# from django.contrib.auth.models import AnonymousUser

# class JWTAuthCookieMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         access_token = request.COOKIES.get("access_token")
#         if access_token:
#             try:
#                 validated_token = JWTAuthentication().get_validated_token(access_token)
#                 user = JWTAuthentication().get_user(validated_token)
#                 request.user = user
#             except Exception as e:
#                 print("Token error: ", str(e))
#                 request.user = AnonymousUser()
#         else:
#             print("no access token in cookies")
#             request.user = AnonymousUser()
