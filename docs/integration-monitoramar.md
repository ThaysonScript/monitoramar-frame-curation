# Integração

O MonitoraMAR já organiza aquisição RTSP, pré-processamento, inferência U-Net/YOLOv8, eventos assíncronos e consumo Web/Mobile.

Este projeto deve entrar como serviço de curadoria, preferencialmente no caminho offline de construção de datasets:

vídeos gravados → curador → manifest + frames → anotação → treinamento.

O sinal de contagem de pessoas via YOLOv8 (inferência apenas, sobre o modelo já em
produção no MonitoraMAR) já pode ser habilitado via `task_aware.people_counting.enabled`
para aumentar o score de criticidade. A integração operacional direta com o serviço de
eventos em tempo real do MonitoraMAR (consumir os eventos já gerados, em vez de
reprocessar os frames offline) continua sendo trabalho futuro.
