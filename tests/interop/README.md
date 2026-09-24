# Testes entre linguagens

`tests/test_interop.py` compila os adaptadores C/C++ quando os compiladores estão disponíveis e confronta exemplos da gramática v0. O Python interno suporta frações arbitrárias; o protocolo FFI restringe a `int64`. Rust precisa de toolchain para verificação CI separada.
