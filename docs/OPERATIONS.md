# Operação do protótipo

Instalação local: criar ambiente isolado, `python -m pip install -e .`, `nabla doctor`; testar `python -m unittest discover -s tests -v`. O SQLite fica em `.nabla/`, sob controle do usuário. Para backup, encerrar escritores, copiar arquivos de banco e conferir um `nabla export` reexecutado; testar recuperação em outro diretório com `nabla import`.

O site estático em `website/` está publicado em <https://3scud3r0.github.io/Nabla-Math/>. Ele exibe métricas versionadas, não participantes conectados. Não há deploy do coordenador: `services/coordinator/app.py` oferece somente uma rota local de health check; não o exponha à internet.

Antes de implantar serviço público, implementar e testar autenticação, retenção, fila durável, observabilidade, limites contra abuso, verificação redundante, backups/restauração e resposta a incidentes. A rotina Hugging Face permanece condicionada a lote aprovado, licença/proveniência revisadas, repositório de destino e credencial de escopo mínimo. Estimar custos de armazenamento, tráfego e inferência antes de ativar qualquer serviço recorrente.
