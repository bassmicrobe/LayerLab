"""Regression checks for GHSA-6q48-6c7w-9gw2; online checks are opt-in."""

from __future__ import annotations

import hashlib
import os
import re
import ssl
import unittest
from pathlib import Path

import certifi
import httpx
import requests


class CertifiSecurityTests(unittest.TestCase):
    def test_installed_certifi_matches_lock_and_security_floor(self):
        lock = (Path(__file__).resolve().parents[1] / "uv.lock").read_text()
        match = re.search(r'name = "certifi"\nversion = "([^"]+)"', lock)
        self.assertIsNotNone(match)
        self.assertEqual(certifi.__version__, match.group(1))
        self.assertGreaterEqual(tuple(map(int, certifi.__version__.split("."))), (2026, 10, 19))

    def test_runtime_install_without_lockfile_has_security_floor(self):
        manifest = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text()
        match = re.search(r'"certifi>=([0-9.]+)"', manifest)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.group(1).split("."))), (2026, 10, 19))

    def test_compromised_root_is_absent_and_verification_remains_enabled(self):
        context = ssl.create_default_context(cafile=certifi.where())
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        roots = context.get_ca_certs()
        self.assertGreater(len(roots), 100)
        # Exact removed emSign ECC Root CA - G3, not the unaffected G1/C1/C3.
        removed = "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b"
        fingerprints = {hashlib.sha256(der).hexdigest() for der in context.get_ca_certs(True)}
        self.assertNotIn(removed, fingerprints)

    @unittest.skipUnless(os.environ.get("CERTIFI_TLS_SMOKE") == "1", "direct online TLS opt-in")
    def test_requests_and_httpx_verify_public_download_origins(self):
        # No environment CA overrides/proxies: this checks the actual bundled roots.
        context = ssl.create_default_context(cafile=certifi.where())
        with (
            requests.Session() as session,
            httpx.Client(verify=context, trust_env=False, timeout=30) as client,
        ):
            session.trust_env = False
            for url in (
                "https://pypi.org/simple/certifi/",
                "https://huggingface.co/",
                "https://dl.fbaipublicfiles.com/",
            ):
                with self.subTest(url=url):
                    with session.get(url, verify=certifi.where(), timeout=30, stream=True) as r:
                        # Some artifact bucket roots deliberately return 403/404.
                        self.assertLess(r.status_code, 500)
                    with client.stream("GET", url) as r:
                        self.assertLess(r.status_code, 500)
                    print(f"Verified TLS with requests and httpx: {url}")
