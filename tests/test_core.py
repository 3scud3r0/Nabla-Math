import json
from fractions import Fraction
from pathlib import Path
import shutil
import tempfile
import unittest

from nablamath.cli import main
from nablamath.expression import DomainError, evaluate, parse_expr
from nablamath.report import write_report
from nablamath.research import calculate
from nablamath.storage import export_verified, load_result, save_result, verify_record


class ResearchTests(unittest.TestCase):
    def test_exact_value_steps_and_condition(self):
        result = calculate("(x+x)/x", {"x": 3})
        self.assertEqual(result.value, 2)
        self.assertEqual([step.rule for step in result.steps],
                         ["soma_de_termos_iguais", "cancelamento_condicional"])
        self.assertEqual(result.to_data()["assumptions"], ["x != 0"])
        self.assertIsNone(result.to_data()["formal_proof"])

    def test_zero_cannot_be_cancelled(self):
        with self.assertRaises(DomainError):
            calculate("(x+x)/x", {"x": 0})

    def test_domain_is_not_erased_by_zero_product(self):
        with self.assertRaises(DomainError):
            calculate("0 * (1/x)", {"x": 0})

    def test_fraction_inputs_are_exact(self):
        result = calculate("1/3 + y", {"y": "2/3"})
        self.assertEqual(result.value, Fraction(1))

    def test_integer_power_and_zero_domain(self):
        self.assertEqual(evaluate(parse_expr("(2/3)**-2"), {}), Fraction(9, 4))
        with self.assertRaises(DomainError):
            evaluate(parse_expr("0**-1"), {})
        with self.assertRaises(DomainError):
            evaluate(parse_expr("0**0"), {})

    def test_float_api_value_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate("x+x", {"x": 0.1})

    def test_parser_rejects_code_and_expensive_inputs(self):
        for expression in ("__import__('os')", "x.__class__", "[x]", "2.5", "2**100", "True"):
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                parse_expr(expression)

    def test_id_and_storage_are_deterministic(self):
        a = calculate("x+x", {"x": 2})
        b = calculate("x+x", {"x": "2"})
        self.assertEqual(a.content_id, b.content_id)
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "a" / "results.sqlite3"
            self.assertTrue(save_result(db, a))
            self.assertFalse(save_result(db, b))
            self.assertEqual(load_result(db, a.content_id)["value"], "4")
            self.assertTrue(verify_record(load_result(db, a.content_id)))
            output = Path(tmp) / "snapshot.jsonl"
            count, digest = export_verified(db, output)
            self.assertEqual(count, 1)
            self.assertEqual(len(digest), 64)
            self.assertEqual(json.loads(output.read_text().splitlines()[0])["content_id"], a.content_id)

    def test_tampered_record_is_rejected(self):
        data = calculate("x+x", {"x": 2}).to_data()
        data["value"] = "999"
        self.assertFalse(verify_record(data))

    def test_similar_source_does_not_collide(self):
        a = calculate("x+x", {"x": 2})
        b = calculate("(x+x)", {"x": 2})
        self.assertNotEqual(a.content_id, b.content_id)

    def test_report_contains_actual_steps_and_limits(self):
        result = calculate("(x+x)/x", {"x": 3})
        with tempfile.TemporaryDirectory() as tmp:
            tex, pdf = write_report(result, Path(tmp) / "report.tex")
            self.assertIsNone(pdf)
            content = tex.read_text(encoding="utf-8")
            self.assertIn(result.content_id, content)
            self.assertIn("cancelamento", content)
            self.assertIn("Sem prova formal Lean", content)
            if shutil.which("pdflatex"):
                try:
                    _, pdf = write_report(result, tex, compile_pdf=True)
                except RuntimeError:
                    self.assertTrue(tex.exists())  # Instalado, mas talvez sem formato/pacotes TeX.
                else:
                    self.assertGreater(pdf.stat().st_size, 1000)

    def test_cli_runs_offline_and_can_read_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "results.sqlite3"
            result = calculate("x+x", {"x": 2})
            self.assertEqual(main(["run", "x+x", "--value", "x=2", "--db", str(db)]), 0)
            self.assertEqual(main(["show", result.content_id, "--db", str(db)]), 0)


if __name__ == "__main__":
    unittest.main()
