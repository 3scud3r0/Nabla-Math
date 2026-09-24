# Banco do coordenador

O protótipo usa o SQLite de `nablamath.coordination.local` e cria as tabelas de fila na
primeira execução. Backups devem copiar o arquivo com o serviço parado ou usando o backup
online do SQLite. O hash dos eventos é verificável, mas não substitui backup, autenticação,
controle de acesso ou consenso entre operadores.
