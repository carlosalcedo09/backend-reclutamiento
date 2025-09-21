from rest_framework import routers

from apps.candidate.views.candidate import CandidateViewSet
from apps.candidate.views.educationCandidate import EducationViewSet
from apps.candidate.views.experienceCandidate import ExperienceViewSet
from apps.candidate.views.skillCandidate import CandidateSkillViewSet
from apps.users.views import UserViewSet
from apps.maintenance.views.skillViews import SkillViewset
router = routers.DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"candidates", CandidateViewSet, basename="candidates")
router.register(r"skills", SkillViewset, basename="skills")
router.register(r"candidate-skills", CandidateSkillViewSet, basename="candidate-skills")
router.register(r"experiences", ExperienceViewSet, basename="experiences")
router.register(r"educations", EducationViewSet, basename="educations")
endpoints = router.urls
