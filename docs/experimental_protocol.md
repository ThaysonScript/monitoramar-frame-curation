# Protocolo experimental

## Fase 1 — Qualidade do dataset (escopo desta aplicação, sem treino)

`monitoramar-compare` roda automaticamente os três métodos sobre o mesmo conjunto de
vídeos:
1. amostragem fixa (`A_fixed_sampling`);
2. amostragem + redundância (`B_temporal_similarity`);
3. embeddings + clustering (`C_visual_diversity`);

Para cada método, `metrics.py` mede, direto do manifest e do `dataset_stats.json`
(sem precisar treinar nada):
- percentual de redução (vs. frames brutos, amostrados e candidatos);
- diversidade (entropia normalizada da distribuição de clusters selecionados);
- custo estimado de anotação (heurística: nº de frames × tempo médio por frame).

A tabela `comparison.csv` permite comparar os três métodos lado a lado nessas
dimensões e já sustenta a hipótese central da proposta (redução de volume sem perda de
diversidade/representatividade).

## Fase 2 — Impacto no treinamento (fora do escopo desta aplicação)

Numa etapa posterior, separada deste repositório: treinar os modelos definidos pelo
projeto com cada um dos datasets gerados na Fase 1 e comparar as métricas adequadas à
tarefa. A divisão treino/validação/teste deve ocorrer
por vídeo/sessão/período/câmera, evitando leakage temporal — os manifests desta
aplicação já preservam `video_id` e `timestamp_seconds` para viabilizar esse split.
