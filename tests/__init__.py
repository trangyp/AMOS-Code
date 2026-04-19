#!/usr/bin/env python3
"""AMOS Testing Framework
=========================

Comprehensive test suite for the AMOS Cognitive Operating System.

Test Categories:
  - unit/         Component-level tests
  - integration/  Cross-component workflow tests
  - system/         End-to-end system tests
  - law/            Global Laws L1-L6 compliance tests
  - security/       Authentication & authorization tests
  - performance/    Benchmarks and load tests

Usage:
  pytest tests/                    # Run all tests
  pytest tests/unit/               # Run unit tests only
  pytest tests/integration/        # Run integration tests
  pytest tests/law/                # Run law compliance tests
  pytest tests/ -v --cov=amos      # With coverage

Requirements:
  pip install pytest pytest-cov pytest-asyncio

Author: Trang Phan
Version: 1.0.0
"""
