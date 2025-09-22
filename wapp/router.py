from rest_framework import routers

from apps.candidate.views import CandidateViewSet
from apps.users.views import UserViewSet
from apps.job.views import JobOffersViewSet, JobApplicationsViewSet

router = routers.DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"candidates", CandidateViewSet, basename="candidates")
router.register(r"joboffers", JobOffersViewSet, basename="joboffers")
router.register(r"jobaplications", JobApplicationsViewSet, basename="jobaplications")
endpoints = router.urls
