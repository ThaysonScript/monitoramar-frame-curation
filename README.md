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

Ou tudo de uma vez:

```bash
pip install -e ".[full]"            # opção A
pip install -r requirements-full.txt    # opção B
```

Sem DINOv2, o pipeline continua funcionando com fallback automático de embedding de
cor e textura.

## Execução

### 1. Curadoria de um conjunto de vídeos

```bash
monitoramar-curate --input data/raw --output data/curated --config configs/default.yaml
```

A saída contém os frames selecionados (`frames/`) e dois manifests em `manifests/`:
`selections.csv` (metadados por frame: cluster e motivo da seleção) e
`dataset_stats.json` (contagens agregadas por vídeo: frames brutos,
amostrados, candidatos e selecionados).

### 2. Relatório de qualidade do dataset (sem treino)

```bash
monitoramar-metrics --dataset data/curated --minutes-per-frame 2.0
```

Calcula, a partir do manifest e do `dataset_stats.json` já produzidos: percentual de
redução (vs. bruto/amostrado/candidatos), diversidade normalizada de clusters e
estimativa de horas de anotação economizadas. Essas métricas avaliam o dataset em si;
o impacto real no treinamento (mAP/mIoU) é avaliado em uma etapa posterior, fora do
escopo desta aplicação.

### 3. Comparação entre estratégias de curadoria

```bash
monitoramar-compare --input data/raw --output data/comparison --config configs/default.yaml
```

Roda automaticamente os três métodos discutidos na proposta sobre o mesmo conjunto de
vídeos — cada um é apenas uma combinação de flags `enabled` do config:

| Método | redundancy | embedding+clustering |
|---|---|---|
| A — Amostragem fixa | desligado | desligado |
| B — Similaridade temporal | ligado | desligado |
| C — Diversidade visual | ligado | ligado |

Gera uma subpasta por método e uma tabela `comparison.csv` na raiz de saída, com as
mesmas métricas do item 2 lado a lado.

### 4. Revisão visual dos frames selecionados

```bash
monitoramar-review --dataset data/curated
```

Gera `data/curated/review/index.html`, uma página local com miniaturas dos frames e
filtros por cluster e motivo de seleção. Abra o arquivo no navegador para revisar a
curadoria antes da anotação humana.

#### Como usar

1. Execute a curadoria normalmente. A visualização depende do arquivo
   `data/curated/manifests/selections.csv` gerado nessa etapa.

   ```bash
   monitoramar-curate --input data/raw --output data/curated --config configs/default.yaml
   ```

2. Gere ou atualize a página de revisão:

   ```bash
   monitoramar-review --dataset data/curated
   ```

3. Abra `data/curated/review/index.html` no navegador. No Windows/PowerShell, também
   é possível executar:

   ```powershell
   Start-Process .\data\curated\review\index.html
   ```

A página não precisa de servidor nem de extensão: funciona localmente. Após uma nova
curadoria, execute novamente `monitoramar-review` para atualizar as miniaturas e os
motivos. Cada cartão usa etiquetas curtas, como `Amostragem fixa`, `Mudança visual` e
`Representa o grupo`.

## Princípios

- Não descartar automaticamente frames visualmente semelhantes.
- Preservar transições e variedade visual.
- Manter rastreabilidade por vídeo, timestamp, cluster e motivo.
- Não usar frames quase idênticos em treino e teste.
- Treinamento e avaliação downstream (mAP/mIoU) ficam fora do escopo desta aplicação;
  aqui o objetivo é produzir e medir a qualidade do dataset curado.
