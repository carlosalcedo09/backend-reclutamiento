from rest_framework import routers

from apps.candidate.views import CandidateViewSet
from apps.users.views import UserViewSet

router = routers.DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"candidates", CandidateViewSet, basename="candidates")

endpoints = router.urls
