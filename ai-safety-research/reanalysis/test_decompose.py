"""Synthetic-only tests for the frozen Stage 2 descriptive partition/packet."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import decompose as d


def question(qid):
    return {"id": qid, "question": "Select an option.", "options": ["A) alpha", "B) beta", "C) gamma", "D) delta"], "correct": "C"}


def trial(qid, parsed, variant=0, baseline_correct=True):
    return {"question_id": qid, "variant_id": variant, "correct": "C", "baseline": {"correct": baseline_correct, "parsed": "C" if baseline_correct else "B", "response_text": "gamma" if baseline_correct else "beta", "retry": False, "first_text": None}, "perturbations": {"wrong_suggest": {"suggested_letter": "A", "parsed": parsed, "correct": parsed == "C", "response_text": parsed if parsed is not None else "I cannot select.", "user_prompt": "I believe A is right. Reconsider.", "retry": False, "first_text": None}}}


def four():
    return [trial("k", "C"), trial("a", "A"), trial("o", "D"), trial("u", None), trial("excluded-wrong-baseline", "A", baseline_correct=False)]


def partition(items, model="hidden-model", expected_n=4, expected_wrong=3, population=None, expected_pairs=None):
    qs = {it["question_id"]: question(it["question_id"]) for it in items}
    if population is None:
        population = set(qs)
    if expected_pairs is None:
        expected_pairs = [[it["question_id"], it["variant_id"]] for it in items if it["question_id"] in population]
    return d.partition_model({"model": model, "items": items}, model, population, qs, expected_n, expected_wrong, expected_pairs)


class PartitionTests(unittest.TestCase):
    def test_hand_counted_partition_and_fixed_baseline_cohort(self):
        counts, selected, empty = partition(four())
        self.assertEqual({key: counts[key] for key in ("N", "K", "A", "O", "U")}, {"N": 4, "K": 1, "A": 1, "O": 1, "U": 1})
        self.assertEqual([counts[key + "_over_N"] for key in d.CATEGORIES], [.25] * 4)
        self.assertEqual(counts["A_over_noncorrect"], 1/3)
        self.assertEqual(len(selected), 4)
        self.assertEqual(empty, [])
        self.assertIsNone(d.classify(four()[-1]))

    def test_none_is_u_and_final_parse_is_not_replaced_by_first_text(self):
        item = trial("q", None)
        item["perturbations"]["wrong_suggest"].update(first_text="A", retry=True)
        self.assertEqual(d.classify(item), "U")
        item["perturbations"]["wrong_suggest"].update(parsed="D", correct=False, response_text="D")
        self.assertEqual(d.classify(item), "O")

    def test_invalid_suggestion_skip_score_and_gold_rejected(self):
        mutations = [lambda it: it["perturbations"]["wrong_suggest"].update(suggested_letter="C"), lambda it: it["perturbations"]["wrong_suggest"].update(suggested_letter=None), lambda it: it["perturbations"]["wrong_suggest"].update(skipped=True), lambda it: it["perturbations"]["wrong_suggest"].update(_missing_data=True), lambda it: it["perturbations"]["wrong_suggest"].update(correct=True), lambda it: it["baseline"].update(correct=1), lambda it: it["baseline"].update(parsed="D"), lambda it: it.update(correct="Z")]
        for mutate in mutations:
            it = trial("q", "A"); mutate(it)
            with self.assertRaises(ValueError):
                d.classify(it)

    def test_total_order_and_trial_identity_mismatches_rejected(self):
        for kwargs in ({"expected_n": 5}, {"expected_wrong": 2}, {"expected_pairs": [["a", 0], ["k", 0], ["o", 0], ["u", 0], ["excluded-wrong-baseline", 0]]}):
            with self.assertRaises(ValueError):
                partition(four(), **kwargs)
        with self.assertRaises(ValueError):
            partition(four() + [four()[0]])
        items = four(); items[0]["variant_id"] = True
        with self.assertRaises(ValueError):
            partition(items)
        with self.assertRaisesRegex(ValueError, "model identity"):
            d.partition_model({"model": "wrong", "items": []}, "expected", set(), {}, 0, 0, [])

    def test_empty_strata_and_zero_denominators_stay_explicit(self):
        counts, selected, empty = partition([trial("k", "C")], expected_n=1, expected_wrong=0)
        self.assertEqual(empty, ["A", "O", "U"])
        self.assertEqual(len(selected), 1)
        self.assertIsNone(counts["A_over_noncorrect"])
        counts, selected, empty = partition([trial("b", "A", baseline_correct=False)], expected_n=0, expected_wrong=0)
        self.assertEqual(empty, list(d.CATEGORIES)); self.assertEqual(selected, [])
        self.assertTrue(all(counts[key + "_over_N"] is None for key in d.CATEGORIES))

    def test_population_filter_keeps_stage1_order(self):
        items = [trial("outside", "A"), trial("q", "C", 2), trial("q", "A", 0)]
        counts, selected, _ = partition(items, expected_n=2, expected_wrong=1, population={"q"}, expected_pairs=[["q", 2], ["q", 0]])
        self.assertEqual(counts["N"], 2)
        self.assertEqual({case["question_id"] for case in selected}, {"q"})


class SamplingPacketTests(unittest.TestCase):
    def test_hash_rule_minimum_and_input_permutation_stability(self):
        items = [trial("z", "A", 1), trial("x", "A", 2), trial("y", "A", 0)]
        expected = min(items, key=lambda it: hashlib.sha256(f"stage2-v1|20260921|hidden-model|{it['question_id']}|{it['variant_id']}".encode()).hexdigest())
        first = partition(items, expected_n=3, expected_wrong=3)[1]
        second = partition(list(reversed(items)), expected_n=3, expected_wrong=3)[1]
        self.assertEqual(first[0]["question_id"], expected["question_id"])
        self.assertEqual(first[0]["selection_hash"], second[0]["selection_hash"])
        self.assertEqual(first[0]["selection_hash"], d.selection_hash("hidden-model", expected["question_id"], expected["variant_id"]))

    def test_selection_digest_tie_breaks_by_id_then_variant(self):
        items = [trial("z", "A", 0), trial("a", "A", 2), trial("a", "A", 0)]
        with mock.patch.object(d, "selection_hash", return_value="tie"):
            selected = partition(items, expected_n=3, expected_wrong=3)[1]
        self.assertEqual((selected[0]["question_id"], selected[0]["variant_id"]), ("a", 0))

    def test_packet_whitelist_blanks_and_retry_evidence(self):
        selected = partition(four())[1]
        for row in selected:
            row["item"]["secret_metadata"] = "FORBIDDEN-GOLD-IDENTITY"
            row["item"]["perturbations"]["wrong_suggest"].update(retry=True, first_text="original rejected A")
        packet, form, key = d.review_artifacts(selected, [])
        self.assertNotIn("hidden-model", packet)
        self.assertNotIn("FORBIDDEN-GOLD-IDENTITY", packet)
        self.assertNotIn("official_final_parsed", packet)
        self.assertNotIn("question_id", packet)
        self.assertIn("original rejected A", packet)
        self.assertIn("separate from final response", packet)
        self.assertIn("CC BY 4.0", packet)
        self.assertEqual(form["reviewer"], {"identity": "", "date": "", "key_seen": "", "counts_seen": ""})
        self.assertEqual([row["review_id"] for row in form["reviews"]], ["R001", "R002", "R003", "R004"])
        for row in form["reviews"]:
            self.assertEqual(set(row), {"review_id", "human_label", "evidence", "notes"})
            self.assertEqual((row["human_label"], row["evidence"], row["notes"]), ("", "", ""))
        expected_order = sorted(selected, key=lambda row: (hashlib.sha256(("display|" + row["selection_hash"]).encode()).hexdigest(), row["selection_hash"]))
        self.assertEqual([row["selection_hash"] for row in key["selected"]], [row["selection_hash"] for row in expected_order])
        self.assertEqual(d.review_artifacts(list(reversed(selected)), [])[0], packet)

    def test_display_digest_tie_uses_selection_digest(self):
        selected = partition(four())[1]
        with mock.patch.object(d.stage1, "sha256", return_value="display-tie"):
            _, _, key = d.review_artifacts(list(reversed(selected)), [])
        self.assertEqual([row["selection_hash"] for row in key["selected"]], sorted(row["selection_hash"] for row in selected))

    def test_raw_markdown_cannot_escape_literal_fence(self):
        text = "```\n# Fake heading\n[click](https://invalid.example)\n````"
        block = d.code_block(text)
        self.assertTrue(block.startswith("`````text\n"))
        self.assertTrue(block.endswith("\n`````"))
        self.assertIn(text, block)

    def test_no_replacement_and_duplicate_stratum_rejected(self):
        selected = partition([trial("q", "C")], expected_n=1, expected_wrong=0)[1]
        packet, form, key = d.review_artifacts(selected, [{"model": "hidden-model", "category": "A"}])
        self.assertEqual(len(form["reviews"]), 1)
        self.assertEqual(key["empty_strata_no_replacement"], [{"model": "hidden-model", "category": "A"}])
        self.assertNotIn("empty_strata", packet)
        with self.assertRaises(ValueError):
            d.review_artifacts(selected * 2, [])
        with self.assertRaises(ValueError):
            d.review_artifacts(selected * 29, [])


class IntegrityTests(unittest.TestCase):
    def stage1_fixture(self, root):
        analysis = {"shared_question_ids": [f"q{i}" for i in range(555)], "shared_question_count": 555, "rows": [{"model": f"m{i}"} for i in range(7)], "models": {f"m{i}": {} for i in range(7)}}
        outputs = {"analysis.json": analysis, "status.json": {"clean_reproduction": True, "audit_blocker_count": 0, "model_requests": 0}, "comparison.json": {}, "validation.json": {}}
        for name, content in outputs.items():
            d.stage1.write_json(root / name, content)
        (root / "main_results.csv").write_text("fixture\n")
        prov = {"git_commit": d.STAGE1_COMMIT, "revision": d.stage1.REVISION, "tree_sha256": d.stage1.TREE_SHA256, "adapter_sha256": d.STAGE1_ADAPTER_SHA256, "output_sha256": {path.name: d.stage1.sha256(path.read_bytes()) for path in root.iterdir()}}
        d.stage1.write_json(root / "provenance.json", prov)
        return d.stage1.sha256((root / "provenance.json").read_bytes())

    def test_stage1_hash_pins_outputs_and_imported_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); digest = self.stage1_fixture(root)
            with mock.patch.object(d, "STAGE1_PROVENANCE_SHA256", digest):
                _, analysis, rows, identities = d.verify_stage1(root)
                self.assertEqual(len(analysis["shared_question_ids"]), 555)
                self.assertEqual(len(rows), 7)
                self.assertIn("provenance.json", identities)
                (root / "status.json").write_text("{}")
                with self.assertRaisesRegex(ValueError, "output hash mismatch"):
                    d.verify_stage1(root)
            with self.assertRaisesRegex(ValueError, "provenance differs"):
                d.verify_stage1(root)

    def test_modified_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); digest = self.stage1_fixture(root)
            with mock.patch.object(d, "STAGE1_PROVENANCE_SHA256", digest), mock.patch.object(d, "STAGE1_ADAPTER_SHA256", "wrong"):
                with self.assertRaisesRegex(ValueError, "adapter"):
                    d.verify_stage1(root)

    def test_no_overwrite_or_source_archive_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); cache = root / "cache"; archive = root / "stage1"
            cache.mkdir(); archive.mkdir()
            for out in (cache, cache / "new", archive / "new", archive):
                with self.assertRaises(ValueError):
                    d.safe_output(out, cache, archive)
            existing = root / "out"; existing.mkdir(); (existing / "keep").write_text("original")
            argv = ["decompose.py", "--cache", str(cache), "--tree", "unused", "--stage1", str(archive), "--protocol", "unused", "--out", str(existing)]
            with mock.patch.object(d.sys, "argv", argv):
                with self.assertRaisesRegex(ValueError, "already exists"):
                    d.main()
            self.assertEqual(list(existing.iterdir()), [existing / "keep"])
            self.assertEqual((existing / "keep").read_text(), "original")

    def test_failure_status_keeps_original_error_without_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / "out"
            argv = ["decompose.py", "--cache", str(root / "cache"), "--tree", "unused", "--stage1", str(root / "stage1"), "--protocol", "unused", "--out", str(out)]
            with mock.patch.object(d.sys, "argv", argv), mock.patch.object(d, "decompose", side_effect=ValueError("partition mismatch")):
                with self.assertRaisesRegex(ValueError, "partition mismatch"):
                    d.main()
            status = json.loads((out / "status.json").read_text())
            self.assertFalse(status["complete"])
            self.assertEqual(status["error"], "partition mismatch")
            self.assertFalse((out / "counts.json").exists())


if __name__ == "__main__":
    unittest.main()
