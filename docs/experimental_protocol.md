# Protocolo experimental

Comparar:
1. amostragem fixa;
2. amostragem + redundância;
3. embeddings + clustering;
4. método completo task-aware.

Medir:
- percentual de redução;
- diversidade;
- cobertura de situações raras;
- tempo de anotação;
- mAP/precision/recall para detecção;
- mIoU/Dice para segmentação.

A divisão treino/validação/teste deve ocorrer por vídeo/sessão/período/câmera, evitando leakage temporal.
