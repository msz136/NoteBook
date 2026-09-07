#!/usr/bin/env python3
"""Unit tests for P0 distribution standardization and validation invariants."""

from __future__ import annotations

import unittest

import numpy as np

from run_experiments import draw_standardized


class DistributionTest(unittest.TestCase):
    def test_frozen_distributions_are_approximately_standardized(self) -> None:
        rng = np.random.default_rng(12345)
        for name in ["normal", "student_t_df3", "centered_lognormal"]:
            sample = draw_standardized(name, rng, (300_000,))
            self.assertLess(abs(float(sample.mean())), 0.025, name)
            self.assertLess(abs(float(sample.var()) - 1.0), 0.10, name)

    def test_unknown_distribution_fails(self) -> None:
        with self.assertRaises(ValueError):
            draw_standardized("unknown", np.random.default_rng(1), (2,))


if __name__ == "__main__":
    unittest.main()
