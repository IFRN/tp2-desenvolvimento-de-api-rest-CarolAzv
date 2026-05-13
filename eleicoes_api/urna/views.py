from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Eleitor, Eleicao, Candidato, AptidaoEleitor, RegistroVotacao, Voto
from .serializers import EleitorSerializer, EleicaoSerializer, CandidatoSerializer, AptidaoEleitorSerializer, RegistroVotacaoSerializer, VotoSerializer, VotacaoInputSerializer


class EleitorViewSet(viewsets.ModelViewSet):
    queryset = Eleitor.objects.all()
    serializer_class = EleitorSerializer
    filterset_fields = ['nome', 'email', 'cpf']
    filter_backends = [filters.SearchFilter]
    search_fields = []
    ordering_fields = []

class EleicaoViewSet(viewsets.ModelViewSet):
    queryset = Eleicao.objects.all()
    serializer_class = EleicaoSerializer
    filterset_fields = ['status', 'tipo', 'criado_por']
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo']
    ordering_fields = ['data_inicio']

class CandidatoViewSet(viewsets.ModelViewSet):
    queryset = Candidato.objects.select_related('eleicao')
    serializer_class = CandidatoSerializer
    filterset_fields = ['eleicao']
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'nome_urna', 'partido_ou_chapa']
    ordering_fields = []

class AptidaoEleitorViewSet(viewsets.ModelViewSet):
    queryset = AptidaoEleitor.objects.select_related('eleitor', 'eleicao')
    serializer_class = AptidaoEleitorSerializer
    filterset_fields = ['eleitor', 'eleicao']
    filter_backends = [filters.SearchFilter]
    search_fields = []
    ordering_fields = []

class RegistroVotacaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegistroVotacao.objects.all()
    serializer_class = RegistroVotacaoSerializer
    filterset_fields = [' eleicao']
    filter_backends = [filters.SearchFilter]
    search_fields = []
    ordering_fields = ['data_hora']

class VotoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Voto.objects.all()
    serializer_class = VotoSerializer
    filterset_fields = ['eleicao']
    filter_backends = [filters.SearchFilter]
    search_fields = []
    ordering_fields = []


router = DefaultRouter()
router.register(r'eleitores', EleitorViewSet)
router.register(r'eleicoes', EleicaoViewSet)
router.register(r'candidatos', CandidatoViewSet)
router.register(r'aptidoes', AptidaoEleitorViewSet)
router.register(r'registros-votacao', RegistroVotacaoViewSet)
router.register(r'votos', VotoViewSet)