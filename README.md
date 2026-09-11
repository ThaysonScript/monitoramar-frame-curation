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

Duas formas equivalentes — escolha uma:

**A) via `pyproject.toml` (recomendado, instala os comandos `monitoramar-*`)**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**B) via `requirements.txt` (sem instalar o pacote/comandos, só as bibliotecas)**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

Nesse caso, rode os módulos diretamente em vez dos comandos `monitoramar-*`, por exemplo:
`python -m monitoramar_curator.cli --input ... --output ... --config ...`

Para DINOv2 (embeddings semânticos):

```bash
pip install -e ".[dinov2]"          # opção A
pip install -r requirements-dinov2.txt  # opção B
```

Para contagem de pessoas via YOLOv8 (sinal task-aware):

```bash
pip install -e ".[yolo]"            # opção A
pip install -r requirements-yolo.txt    # opção B
```

Ou tudo de uma vez:

```bash
pip install -e ".[full]"            # opção A
pip install -r requirements-full.txt    # opção B
```

Sem essas dependências, o pipeline continua funcionando com fallback automático
(embedding de cor/textura no lugar do DINOv2; `people_count=None` no lugar do YOLOv8).

## Execução

### 1. Curadoria de um conjunto de vídeos

```bash
monitoramar-curate --input data/raw --output data/curated --config configs/default.yaml
```

A saída contém os frames selecionados (`frames/`) e dois manifests em `manifests/`:
`selections.csv` (metadados por frame: cluster, event_score, people_count, motivo da
seleção) e `dataset_stats.json` (contagens agregadas por vídeo: frames brutos,
amostrados, candidatos e selecionados).

### 2. Relatório de qualidade do dataset (sem treino)

```bash
monitoramar-metrics --dataset data/curated --minutes-per-frame 2.0
```

Calcula, a partir do manifest e do `dataset_stats.json` já produzidos: percentual de
redução (vs. bruto/amostrado/candidatos), diversidade normalizada de clusters,
cobertura de eventos críticos, nº de contagens de pessoas distintas cobertas e
estimativa de horas de anotação economizadas. Essas métricas avaliam o dataset em si;
o impacto real no treinamento (mAP/mIoU) é avaliado em uma etapa posterior, fora do
escopo desta aplicação.

### 3. Comparação entre estratégias de curadoria

```bash
monitoramar-compare --input data/raw --output data/comparison --config configs/default.yaml
```

Roda automaticamente os quatro métodos discutidos na proposta sobre o mesmo conjunto de
vídeos — cada um é apenas uma combinação de flags `enabled` do config:

| Método | redundancy | embedding+clustering | task_aware |
|---|---|---|---|
| A — Amostragem fixa | desligado | desligado | desligado |
| B — Similaridade temporal | ligado | desligado | desligado |
| C — Diversidade visual | ligado | ligado | desligado |
| D — Task-aware (proposto) | ligado | ligado | ligado |

Gera uma subpasta por método e uma tabela `comparison.csv` na raiz de saída, com as
mesmas métricas do item 2 lado a lado.

## Task-aware: contagem de pessoas via YOLOv8

Para ativar o sinal que diferencia a curadoria de um dedup genérico (seção 7 da
proposta), habilite em `configs/default.yaml`:

```yaml
task_aware:
  people_counting:
    enabled: true
    model: yolov8n.pt   # ou o modelo já treinado/usado em produção no MonitoraMAR
```

O YOLOv8 é usado apenas para **inferência** sobre os frames candidatos (contar
banhistas), nunca para treino — o objetivo é usar o modelo já existente como sinal de
seleção. Se `ultralytics` não estiver instalado, ou a flag estiver desligada,
`people_count` fica `None` e o `event_score` passa a depender só da novidade de
embedding (comportamento anterior, sem quebrar o pipeline).

## Princípios

- Não descartar automaticamente frames visualmente semelhantes.
- Preservar transições, casos raros e situações críticas.
- Manter rastreabilidade por vídeo, timestamp, cluster e motivo.
- Não usar frames quase idênticos em treino e teste.
- Inferências YOLO/U-Net são sinais de curadoria, não ground truth.
- Treinamento e avaliação downstream (mAP/mIoU) ficam fora do escopo desta aplicação;
  aqui o objetivo é produzir e medir a qualidade do dataset curado.
