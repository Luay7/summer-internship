# Day 4: AI-Assisted Debugging Plan & Log

## Overview
This document outlines the strategy for intentionally introducing 5 distinct bugs into the `checker.py` script. The goal is to simulate real-world debugging scenarios, analyze their symptoms, and utilize an AI coding assistant to diagnose and resolve them iteratively.

## Phase 1: The Bug Injection Plan (Initial Strategy)

Before writing any code, here is the planned roadmap of the bugs that will be injected, their types, and the expected disruption they will cause:

### 1. CLI Setup
* **Bug Type:** Input Error
* **Intentional Modification:** Delete `--delay` argument from `argparse`
* **Expected Symptom / Impact:** Immediate `AttributeError` crash upon execution.
* **Severity:** High

### 2. URL Validation
* **Bug Type:** Logic Error
* **Intentional Modification:** Reverse the `http/https` validation condition
* **Expected Symptom / Impact:** Rejects valid URLs and attempts to process invalid ones.
* **Severity:** High

### 3. Link Extraction
* **Bug Type:** Performance
* **Intentional Modification:** Remove duplicate filtering (`in` list check)
* **Expected Symptom / Impact:** Endless redundant scanning of duplicate links on the same page.
* **Severity:** Low

### 4. Network Request (Timeout False-Positives)
* **Bug Type:** Network Error
* **Intentional Modification:** Change `timeout=5` to `timeout=0.001`
* **Expected Symptom / Impact:** Massive false-positive timeouts; marks all links as `[DEAD]`.
* **Severity:** High

### 5. Network Request (Infinite Hang)
* **Bug Type:** Hang Error
* **Intentional Modification:** Remove `timeout` parameter completely
* **Expected Symptom / Impact:** Infinite hang (freeze) if the target server does not respond.
* **Severity:** Critical

---

## Phase 2: Execution & Resolution Log
*(This section will be iteratively updated as bugs are injected into the code, diagnosed by the AI, and fixed).*

**Status:** Ready to begin iterative injection.
