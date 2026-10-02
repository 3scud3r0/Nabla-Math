# Política de releases e compatibilidade

## Versionamento

O pacote segue SemVer. Enquanto a versão for `0.x`, mudanças incompatíveis exigem
incremento *minor* e nota de migração. Releases estáveis `1.x` não podem quebrar a
API pública ou schemas persistidos sem incremento *major*. Versões alpha/beta não
são indicadas para operação crítica.

São contratos públicos: nomes presentes em `__all__`, comandos documentados da
CLI, schemas JSON publicados, formatos SQLite versionados e códigos de saída. Um
módulo interno não é contrato apenas por ser importável.

## Suporte

A fonte normativa legível por máquina é `src/nablamath/compatibility.json`, enviada
no wheel. A documentação deve reproduzir, e nunca ampliar, essa matriz. Cada versão
publicada recebe correções críticas de segurança até ser substituída por outra
versão da mesma linha; a linha alpha atual não possui garantia temporal de suporte.

Depreciações em release estável devem:

1. emitir aviso com substituição e versão prevista de remoção;
2. permanecer durante pelo menos um incremento *minor*;
3. incluir teste de compatibilidade e nota de migração;
4. nunca reinterpretar silenciosamente dados persistidos.

## Checklist obrigatório

1. CI completa verde nas versões e sistemas declarados.
2. Instalação limpa de wheel e source distribution em ambiente vazio.
3. Testes de upgrade, migração, backup e restauração para formatos persistidos.
4. Changelog com mudanças de API, schema, segurança, dados e limitações.
5. Artefatos construídos uma vez, hashes publicados e conteúdo do wheel auditado.
6. Credenciais ausentes e dependências revisadas.
7. Tag assinada pelo mantenedor autorizado, quando a infraestrutura de assinatura
   estiver estabelecida.
8. Rollback ensaiado antes de ativar publicação, coordenação ou migrations.

## Responsabilidade e rollback

O responsável que autoriza a release deve ser registrado nas notas da versão. Uma
falha de integridade, migração ou segurança interrompe a distribuição; a versão é
retirada, o incidente é registrado e a recuperação segue `INCIDENT_RESPONSE.md`.
Rollback de schema restaura backup verificado: nunca se tenta rebaixar dados por
uma transformação destrutiva improvisada.
