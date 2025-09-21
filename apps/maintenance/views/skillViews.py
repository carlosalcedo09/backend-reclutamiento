from rest_framework import viewsets
from apps.maintenance.models import Skill
from apps.maintenance.serializers import SkillSerializer
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class SkillViewset(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
