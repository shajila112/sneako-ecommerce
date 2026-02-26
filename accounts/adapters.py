from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        print("🔥 pre_social_login triggered")

        # Email from Google
        email = sociallogin.account.extra_data.get("email")
        print("👉 Google Email:", email)

        if not email:
            print("❌ No email returned from Google")
            return

        try:
            user = User.objects.get(email=email)
            print("✅ Existing user found:", user)

            # Link Google account to existing user
            sociallogin.connect(request, user)

        except User.DoesNotExist:
            print("🆕 New user — will create automatically")

    def is_open_for_signup(self, request, sociallogin):
        print("🟢 Signup allowed")
        return True
