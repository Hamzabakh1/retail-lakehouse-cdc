import tempfile
import unittest
from pathlib import Path

from retail_lakehouse.pipeline import SAMPLE_EVENTS, run, transform


class RetailLakehouseTests(unittest.TestCase):
    def test_deduplicates_and_quarantines_invalid_event(self) -> None:
        silver, quarantine, gold = transform(SAMPLE_EVENTS)
        self.assertEqual(3, len(silver))
        self.assertEqual(1, len(quarantine))
        self.assertEqual(2, len(gold))
        self.assertEqual(425.4, sum(row["gross_sales"] for row in gold))

    def test_run_persists_a_reconciled_audit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audit = run(Path(directory))
            self.assertEqual("passed", audit["reconciliation_status"])
            self.assertTrue((Path(directory) / "gold_daily_sales.json").exists())
