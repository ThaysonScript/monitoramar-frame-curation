# Arquitetura

O curador é um serviço offline/desacoplado para transformar gravações contínuas em um conjunto reduzido e rastreável de frames para anotação.

1. Extração/amostragem temporal.
2. Filtro barato de redundância.
3. Embeddings visuais.
4. Clustering e representantes.
5. Priorização orientada à tarefa.
6. Persistência do dataset e manifest.
7. Anotação humana.
8. Treinamento/atualização.

A integração futura deve consumir sinais estruturados de YOLO/U-Net sem transformar suas previsões em ground truth.
