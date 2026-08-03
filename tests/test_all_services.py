import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.test_auth_service import test_auth_and_user_flow
from tests.test_media_pipeline import test_media_pipeline_flow
from tests.test_transcript_engine import test_transcript_engine_flow
from tests.test_voice_dna_and_memory import test_voice_dna_and_memory_flow
from tests.test_generation_engine import test_generation_engine_flow
from tests.test_export_engine import test_export_engine_flow
from tests.test_billing_service import test_billing_and_quota_flow


def run_master_test_suite():
    print("=" * 65)
    print("[MASTER TEST] RUNNING SCRIPTLOOM MASTER INTEGRATION TEST SUITE")
    print("=" * 65)

    print("\n[SECTION 1] Testing Authentication & User Management...")
    test_auth_and_user_flow()

    print("\n[SECTION 2] Testing Upload & Media Processing Pipeline...")
    test_media_pipeline_flow()

    print("\n[SECTION 3] Testing Speech-to-Text & Transcript Engine...")
    test_transcript_engine_flow()

    print("\n[SECTION 4] Testing Voice DNA Engine & Creator Memory RAG Store...")
    test_voice_dna_and_memory_flow()

    print("\n[SECTION 5] Testing AI Generation Engine & Prompt Orchestrator...")
    test_generation_engine_flow()

    print("\n[SECTION 6] Testing Content Management & Export Engine...")
    test_export_engine_flow()

    print("\n[SECTION 7] Testing Billing & Usage System...")
    test_billing_and_quota_flow()

    print("\n" + "=" * 65)
    print("[SUCCESS] MASTER TEST SUITE PASSED! ALL 7 SECTIONS VERIFIED CLEANLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_master_test_suite()
