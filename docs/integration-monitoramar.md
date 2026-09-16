# Integração

O MonitoraMAR já organiza aquisição RTSP, pré-processamento, inferência, eventos assíncronos e consumo Web/Mobile.

Este projeto deve entrar como serviço de curadoria, preferencialmente no caminho offline de construção de datasets:

vídeos gravados → curador → manifest + frames → anotação → treinamento.

A integração operacional direta com o serviço de eventos em tempo real do MonitoraMAR
(consumir os eventos já gerados, em vez de reprocessar os frames offline) continua
sendo trabalho futuro.
