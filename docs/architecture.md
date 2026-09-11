# Arquitetura

O curador é um serviço offline/desacoplado para transformar gravações contínuas em um conjunto reduzido e rastreável de frames para anotação.

1. Extração/amostragem temporal.
2. Filtro barato de redundância (opcional, `redundancy.enabled`).
3. Embeddings visuais (opcional, `embedding.enabled` + `clustering.enabled`; DINOv2 com
   fallback para histograma de cor/textura se `torch` não estiver instalado).
4. Clustering e seleção de N representantes por cluster (`selection.representatives_per_cluster`).
5. Priorização orientada à tarefa: contagem de pessoas via YOLOv8 (inferência apenas,
   opcional, `task_aware.people_counting.enabled`) + novidade de embedding, combinadas
   em `event_score`.
6. Persistência do dataset, manifest (`selections.csv`) e estatísticas agregadas
   (`dataset_stats.json`).
7. Métricas de qualidade do dataset (`monitoramar-metrics`) e comparação entre
   estratégias (`monitoramar-compare`) — ambas sem depender de treino.
8. Anotação humana.
9. Treinamento/atualização (fora do escopo desta aplicação).

Cada estágio 2–5 pode ser ligado/desligado via config; essa é a base do harness de
comparação entre os métodos A (amostragem fixa), B (similaridade temporal), C
(diversidade visual) e D (task-aware, proposto).

A inferência de YOLO/U-Net é sempre tratada como sinal de curadoria, nunca como
ground truth.
