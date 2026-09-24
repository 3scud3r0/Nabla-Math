# Modelo de ameaças inicial

| Superfície | Risco | Controle já presente | Ainda necessário |
| --- | --- | --- | --- |
| Expressões | Execução de código disfarçada de cálculo | AST Python em modo restrito, sem `eval`, limites de profundidade/tamanho | Revisão e fuzzing contínuos |
| Dados locais | Registros adulterados | Hash, SQLite, reexecução antes de exportar/importar | Assinatura/autoria verificável e backup |
| Agentes | Código e prompts hostis | Protocolo declarativo e recusa de código arbitrário | Sandboxing real antes de permitir outra linguagem |
| Tarefas globais | Trabalhadores simulados, spam, conluio | Coordenador **local** reexecuta resultado e requer dois IDs | Identidade forte, cotas e revisores independentes |
| Publicação | Licença incorreta, dados privados, vazamento de avaliação | Lote local, licença/proveniência declaradas, cartão e divisões | Política jurídica, revisão humana, testes de vazamento |
| Infraestrutura | Credenciais vazadas e indisponibilidade | Nenhuma credencial no código | Segredos de deploy, observabilidade, backups, rotação |

Dois IDs textuais de trabalhador não equivalem a dois participantes independentes. Hash garante integridade frente a alterações, não autoria nem confiabilidade da fonte.
