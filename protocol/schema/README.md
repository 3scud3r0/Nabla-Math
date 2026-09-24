# Protocolo NablaMath v1

O envelope intercambiável é JSON UTF-8 canônico: chaves ordenadas, separadores compactos,
números exatos como strings (`"3/2"`) e arrays com ordem semântica preservada. Todo registro
tem `schema_version`, `content_id`, `payload`, `provenance`, `license` e `evidence`. Valores
de ponto flutuante devem carregar tolerância e unidade. A identidade é SHA-256 do envelope
canônico; ela não prova autoria nem validade científica.
