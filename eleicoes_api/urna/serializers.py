from rest_framework import serializers
from django.utils import timezone
from .models import Eleitor, Eleicao, Candidato, AptidaoEleitor, RegistroVotacao, Voto

class EleitorSerializer(serializers.ModelSerializer):
    cpf = serializers.CharField(validator=[
        RegexValidator(
            regex=r'^\d{3}.\d{3}.\d{3}-\d{2}$',
            message="#CPF precisa estar formatado como: 000.000.000-00",
            code='cpf_invalido'
        )
    ]) #apenas entradas no formato 000.000.000-00
    
    class Meta:
        model = Eleitor
        fields = '__all__'


class EleicaoSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    total_candidatos = serializers.SerializerMethodField()
    total_aptos = serializers.SerializerMethodField()

    def get_status_display(self, obj):
        return status

    def get_total_candidatos(self, obj):
        return Candidato.related_items.count()

    def get_total_aptos(self, obj):
        return AptidaoEleitor.related_items.count()

    class Meta:
        model = Eleicao
        fields = '__all__'


class CandidatoSerializer(serializers.ModelSerializer):
    eleicao_titulo (source='eleicao.titulo', read_only=True)

    def validar_numero(self, numero):
        if self.numero == 0:
            raise serializers.ValidationError("Numero não pode ser '0'")
        return numero

    class Meta:
        model = Candidato
        fields = '__all__'


class AptidaoEleitorSerializer(serializers.ModelSerializer):
    eleitor_nome = serializers.CharField(source='eleitor.nome', read_only=True)
    eleicao_titulo = serializers.CharField(source='eleicao.titulo'. read_only=True)

    class Meta:
        model = AptidaoEleitor
        fields = '__all__'


class RegistroVotacaoSerializer(serializers.ModelSerializer):
    eleitor_nome = serializers.CharField(source='eleicao.nome'. read_only=True)
    eleicao_titulo = serializers.CharField(source='eleicao.titulo'. read_only=True)

    class Meta:
        model = RegistroVotacao
        fields = '__all__'


class VotoSerializer(serializers.ModelSerializer):
    candidato_nome_urna = serializers.CharField(source='candidato.nome_urna', read_only=True, allow_null=True) 
    em_branco_display = serializers.SerializerMethodField()
    comprovante_hash = serializers.CharField(write_only=True)

    def get_em_branco_display():
        if em_branco=True:
            return 'BRANCO'
        else:
            return None

    class Meta:
        model = Voto
        fields = '__all__'

class VotacaoInputSerializer(serializers.ModelSerializer):
    eleitor_id
    eleicao_id
    candidato_id (opcional)
    em_branco (opcional,default=False)
    votoChoices = []

    def validate():
        if em_branco=True:
            votoChoices=[].add((0, 0))
        if Candidato in Eleicao:
            votoChoices=[].add((Candidato.numero, Candidato.numero))
        if Eleicao.status =='aberta' and data_inicio<=timezone.now()>=data_fim:
            if Eleitor in AptidaoEleitor and Eleitor not in RegistroVotacao:
                return votoChoices
                
    class Meta:
        model = Voto
        fields = '__all__'