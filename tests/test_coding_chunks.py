"""Regresiones de fragmentos breves y conservación de la procedencia."""

import json
import unittest

from features.coding_chunks import (
    WORD_RE,
    paragraph_blocks,
    paragraph_fragments,
    text_sha256,
)


class CodingChunksTestCase(unittest.TestCase):
    def blocks(self, text):
        paragraphs = paragraph_fragments(text)
        for number, paragraph in enumerate(paragraphs, 1):
            paragraph["paragraph_number"] = number
        blocks = paragraph_blocks(paragraphs, 50, 100, 150)
        # Cada palabra aparece una vez y cada segmento remite al texto original.
        self.assertEqual(
            WORD_RE.findall(text),
            [word for block in blocks for word in WORD_RE.findall(block["content"])],
        )
        for block in blocks:
            for segment in json.loads(block["source_segments_json"]):
                original = text[segment["source_start_char"]:segment["source_end_char"]]
                self.assertEqual(text_sha256(original), segment["content_sha256"])
        return blocks

    def test_short_middle_paragraph_joins_shorter_neighbor(self):
        text = "\n\n".join("palabra " * n for n in (121, 33, 138))
        self.assertEqual([b["n_words"] for b in self.blocks(text)], [154, 138])

    def test_short_leading_paragraph_and_tail_are_absorbed(self):
        for sizes, expected in [((5, 150), [155]), ((141, 13), [154]),
                                ((49, 150, 49), [248]), ((150, 2), [152])]:
            with self.subTest(sizes=sizes):
                text = "\n\n".join("palabra " * n for n in sizes)
                self.assertEqual([b["n_words"] for b in self.blocks(text)], expected)

    def test_word_split_remainder_is_preserved(self):
        self.assertEqual([b["n_words"] for b in self.blocks("palabra " * 314)], [150, 164])

    def test_whole_short_utterance_stays_separate(self):
        self.assertEqual([b["n_words"] for b in self.blocks("Es un acuerdo de Comités.")], [5])
        self.assertEqual(self.blocks(""), [])


if __name__ == "__main__":
    unittest.main()
