# Integração

O MonitoraMAR já organiza aquisição RTSP, pré-processamento, inferência U-Net/YOLOv8, eventos assíncronos e consumo Web/Mobile.

Este projeto deve entrar como serviço de curadoria, preferencialmente no caminho offline de construção de datasets:

vídeos gravados → curador → manifest + frames → anotação → treinamento.

No futuro, eventos e inferências estruturadas podem ser consumidos para aumentar o score de criticidade.
