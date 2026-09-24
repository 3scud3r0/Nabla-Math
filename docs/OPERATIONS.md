# Operação do protótipo

Instalação local: criar ambiente isolado, `python -m pip install -e .`, `nabla doctor`; testar `python -m unittest discover -s tests -v`. O SQLite fica em `.nabla/`, sob controle do usuário. Para backup, encerrar escritores, copiar arquivos de banco e conferir um `nabla export` reexecutado; testar recuperação em outro diretório com `nabla import`.

Não existe deploy da coordenação. O site em `website/` é estático e publica métricas versionadas quando GitHub Pages for configurado; métricas zero são intencionais. Antes de serviço público, implementar autenticação, retenção, fila robusta, observabilidade, limitação de abuso, replicação e plano de incidentes. Uma rotina diária de publicação exigirá conta, licença, revisão e credenciais de escopo mínimo. Documentar custos de armazenamento, tráfego e inferência antes de ativá-la.
