from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import hashlib

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

    @action(detail=True, methods=["POST"])
    def registrar_voto(self, request, pk=None):
        eleicao = self.get_object()
        data = request.data
        eleitor_id = data.get('eleitor_id')
        candidato_id = data.get('candidato_id')
        em_branco = data.get('em_branco', False)

        try:
            eleitor = Eleitor.objects.get(id=eleitor_id)
        except Eleitor.DoesNotExist:
            return Response({"error": "Eleitor não encontrado"}, status=400)

        if not AptidaoEleitor.objects.filter(eleitor=eleitor, eleicao=eleicao).exists():
            return Response({"error": "Eleitor não apto para esta eleição"}, status=400)

        if RegistroVotacao.objects.filter(eleitor=eleitor, eleicao=eleicao).exists():
            return Response({"error": "Eleitor já votou nesta eleição"}, status=400)

        if eleicao.status != 'aberta' or not (eleicao.data_inicio <= timezone.now() <= eleicao.data_fim):
            return Response({"error": "Eleição não está aberta"}, status=400)

        candidato = None
        if not em_branco:
            try:
                candidato = Candidato.objects.get(id=candidato_id, eleicao=eleicao)
            except Candidato.DoesNotExist:
                return Response({"error": "Candidato inválido"}, status=400)

        RegistroVotacao.objects.create(eleitor=eleitor, eleicao=eleicao)
        token = hashlib.sha256(f"{eleitor.id}{eleicao.id}{timezone.now()}".encode()).hexdigest()
        voto = Voto.objects.create(eleicao=eleicao, candidato=candidato, em_branco=em_branco, comprovante_hash=token)
        candidato_nome = candidato.nome_urna if candidato else "EM BRANCO"

        return Response({
            "mensagem": "Voto registrado com sucesso. Guarde o seu comprovante.",
            "comprovante": {
                "token": token,
                "eleicao": eleicao.titulo,
                "candidato": candidato_nome,
                "data_hora": voto.data_hora.isoformat(),
                "qr_code_url": f"/eleicoes_api/comprovantes/qr/?token={token}"
            }
        })

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


@api_view(['GET']) #/eleicoes_api/verificar-comprovante/?token=<TOKEN>
def verificar_comprovante(request):
    token = request.GET.get('token')

    try:
        voto = Voto.objects.get(comprovante_hash=token)
        candidato_nome = voto.candidato.nome_urna if voto.candidato else "EM BRANCO"
        return Response({
            "eleicao": voto.eleicao.titulo,
            "candidato": candidato_nome,
            "data_hora": voto.data_hora.isoformat()
        })


router = DefaultRouter()
router.register(r'eleitores', EleitorViewSet)
router.register(r'eleicoes', EleicaoViewSet)
router.register(r'candidatos', CandidatoViewSet)
router.register(r'aptidoes', AptidaoEleitorViewSet)
router.register(r'registros-votacao', RegistroVotacaoViewSet)
router.register(r'votos', VotoViewSet)