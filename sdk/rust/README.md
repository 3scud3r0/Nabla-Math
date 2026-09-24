# SDK Rust experimental

`cargo test --manifest-path sdk/rust/Cargo.toml` verifica a gramática racional v0 sem dependências externas. Há apenas leitura de frações canônicas `int64`; integração com Lean, Python e conceitos físicos ainda exige contratos próprios. O compilador Rust não está instalado em todos os ambientes locais; a CI de interoperabilidade verifica este crate quando disponível.
