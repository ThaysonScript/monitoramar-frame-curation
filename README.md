# MonitoraMAR Frame Curation

Pipeline de curadoria inteligente de frames para construção de datasets a partir de vídeos contínuos.

```text
NOVOS VÍDEOS
    │
    ▼
Extração de frames
    │
    ▼
Amostragem temporal
    │
    ▼
Filtro de redundância
    │
    ▼
Embeddings visuais
    │
    ▼
Clustering / diversidade
    │
    ▼
Análise orientada à tarefa
    │
    ├───────────────┐
    ▼               ▼
Frames comuns   Frames críticos
    │               │
    └───────┬───────┘
            ▼
       Dataset final
            │
            ▼
         Anotação
            │
            ▼
Treinamento / atualização
```

## Objetivo

Reduzir a redundância antes da anotação, preservando diversidade visual e situações relevantes para as tarefas de visão computacional do MonitoraMAR.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Para DINOv2:

```bash
pip install -e ".[dinov2]"
```

## Execução

```bash
monitoramar-curate --input data/raw --output data/curated --config configs/default.yaml
```

A saída contém frames, embeddings/manifests e relatório.

## Princípios

- Não descartar automaticamente frames visualmente semelhantes.
- Preservar transições, casos raros e situações críticas.
- Manter rastreabilidade por vídeo, timestamp, cluster e motivo.
- Não usar frames quase idênticos em treino e teste.
- Inferências YOLO/U-Net são sinais de curadoria, não ground truth.
