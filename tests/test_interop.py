from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("cc") and shutil.which("c++"), "Compiladores C/C++ opcionais")
class InteropTests(unittest.TestCase):
    def test_c_and_cpp_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / "main.cpp").write_text('''
#include "nabla_fraction.hpp"
#include <cassert>
int main() {
    auto x = nabla::parse_fraction("-3/4");
    assert(x && x->numerator == -3 && x->denominator == 4);
    for (auto s : {"00", "-0", "+1", "2/4", "3/1", "1/0", " 1", "1/02"})
        assert(!nabla::parse_fraction(s));
    assert(nabla::parse_fraction("0"));
}
''', encoding="utf-8")
            compile_c = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-c",
                         str(ROOT / "sdk/c/nabla_fraction.c"), "-o", str(work / "fraction.o")]
            compile_cpp = ["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                           "-I", str(ROOT / "sdk/cpp"), str(work / "main.cpp"),
                           str(work / "fraction.o"), "-o", str(work / "check")]
            for command in (compile_c, compile_cpp):
                completed = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)
            subprocess.run([str(work / "check")], check=True, capture_output=True)
