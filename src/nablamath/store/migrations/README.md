# Migrações SQLite

`schema_version=1` é a única versão aceitada pelo leitor atual. Não sobrescreva um registro existente: exporte e revalide o lote original, construa um banco novo para a versão seguinte e guarde as ligações de IDs antigos/novos. A migração deve ser transacional, reversível por backup e testada com casos de falha. Não existe migração automática para esquema ainda não definido.
