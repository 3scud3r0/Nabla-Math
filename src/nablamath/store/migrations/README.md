# Migrações SQLite

`PRAGMA user_version=1` é a versão atual. `migrate()` aplica `0001_initial.py`
de forma idempotente a bancos alpha com versão zero e recusa versões futuras. Toda
próxima migração deve ter número monotônico, executar em transação, preservar IDs e
incluir fixtures de upgrade e falha. Use `store.backup.backup_database` antes de
migrar e `restore_database` para recuperação verificada por hash; restauração nunca
sobrescreve um banco existente.
