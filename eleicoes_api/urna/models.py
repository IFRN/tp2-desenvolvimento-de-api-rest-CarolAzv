from django.db import models

class Eleitor(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True) # Formato 000.000.000-00
    data_nascimento = models.DateField()
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

class Eleicao(models.Model):
    tipoChoices = [
        ("estudantil", "ESTUDANTIL"),
        ("sindical", "SINDICAL"),
        ("associacao", "ASSOCIAÇÃO"),
        ("condominio", "CONDOMÍNIO"),
        ("conselho", "CONSELHO"),
        ("outra", "OUTRA"),
    ]
    statusChoices = [
        ("rascunho", "RASCUNHO"),
        ("aberta", "ABERTA"),
        ("encerrada", "ENCERRADA"),
        ("apurada", "APURADA"),
    ]
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(choices=tipoChoices)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    status = models.CharField(choices=statusChoices, default="rascunho")
    permite_branco = models.BooleanField(default=True)
    criada_por = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='eleicoes_criadas') # administrador responsável

    def clean(self):
        if self.data_inicio > self.data_fim:
            raise ValidationError({
                "data_fim": "Data final não pode ser antes da data inicial"
            })

class Candidato(models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='candidatos')
    numero = models.PositiveIntegerField() # Número de exibição do candidato
    nome = models.CharField(max_length=150)
    nome_urna = models.CharField(max_length=50)
    partido_ou_chapa = models.CharField(max_length=100, blank=True)
    proposta = models.TextField(blank=True)
    foto_url = models.URLField(blank=True)

    def Meta(self): 
        unique_together = [('eleicao', 'numero')] # números são únicos POR eleição.

class AptidaoEleitor(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='aptidoes')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='aptos')
    data_inclusao = models.DateTimeField(auto_now_add=True)

    def Meta(self): 
        unique_together = [('eleitor', 'eleicao')] # um eleitor só deve ser cadastrado uma vez como apto por eleição.

class RegistroVotacao(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='registros_votacao')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='registros_votacao')
    data_hora = models.DateTimeField(auto_now_add=True)

    def  Meta(self): 
        unique_together = [('eleitor', 'eleicao')] # garantia em nível de banco de que ninguém vota duas vezes na mesma eleição.

class Voto(models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='votos')
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT, related_name='votos', null=True, blank=True) # nulo quando o voto é em branco
    em_branco = models.BooleanField(default=False)
    data_hora = models.DateTimeField(auto_now_add=True)
    comprovante_hash = models.CharField(max_length=64, unique=True) # SHA-256 do token entregue ao eleitor

    def clean():
        if em_branco==True and candidato==None: #Os dois casos mutuamente exclusivos.
            raise ValidationError({
                "(candidato": "Voto em branco não pode ser a um candidato"
            })
        if em_branco==False and candidato is not None:
            raise ValidationError({
                "(candidato": "Votos não em branco precisam ser a um candidato"
            })