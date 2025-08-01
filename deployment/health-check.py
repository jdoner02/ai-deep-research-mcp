#!/usr/bin/env python3
"""
Health Check Script for AI Deep Research MCP Production Deployment

Monitors system health, performance, and functionality to ensure
the platform is operating correctly in production.
"""

import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.presentation.web_interface import WebInterfaceHandler
    from src.domain.entities import ResearchQuery, QueryId, ResearchQueryType
    from src.application.scholarly_use_cases import ScholarlyResearchUseCase
    from src.infrastructure.repositories import (
        InMemoryResearchQueryRepository,
        InMemoryResearchResultRepository,
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)


class HealthChecker:
    """Production health checker for AI Deep Research MCP."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "checks": {},
        }

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return results."""
        print("🏥 AI Deep Research MCP - Health Check")
        print("====================================")

        checks = [
            ("Core Module Imports", self.check_imports),
            ("Domain Layer Health", self.check_domain_layer),
            ("Application Layer Health", self.check_application_layer),
            ("Infrastructure Layer Health", self.check_infrastructure_layer),
            ("Web Interface Health", self.check_web_interface),
            ("Citation Export Functionality", self.check_citation_export),
            ("System Performance", self.check_performance),
            ("File System Health", self.check_file_system),
            ("Git Repository Status", self.check_git_status),
        ]

        passed = 0
        total = len(checks)

        for check_name, check_func in checks:
            print(f"\n🔍 Running: {check_name}")
            try:
                start_time = time.time()
                result = check_func()
                duration = time.time() - start_time

                if result["status"] == "PASS":
                    print(f"✅ PASS - {result['message']} ({duration:.2f}s)")
                    passed += 1
                elif result["status"] == "WARN":
                    print(f"⚠️  WARN - {result['message']} ({duration:.2f}s)")
                    passed += 0.5
                else:
                    print(f"❌ FAIL - {result['message']} ({duration:.2f}s)")

                self.results["checks"][check_name] = {
                    **result,
                    "duration_seconds": round(duration, 2),
                }

            except Exception as e:
                print(f"❌ ERROR - {str(e)}")
                self.results["checks"][check_name] = {
                    "status": "ERROR",
                    "message": str(e),
                    "duration_seconds": 0,
                }

        # Calculate overall status
        pass_rate = passed / total
        if pass_rate >= 0.9:
            self.results["overall_status"] = "HEALTHY"
        elif pass_rate >= 0.7:
            self.results["overall_status"] = "WARNING"
        else:
            self.results["overall_status"] = "CRITICAL"

        self.results["pass_rate"] = pass_rate
        self.results["passed_checks"] = passed
        self.results["total_checks"] = total

        return self.results

    def check_imports(self) -> Dict[str, str]:
        """Check that all critical modules can be imported."""
        try:
            # Test critical imports
            from src.domain.entities import ResearchQuery, ResearchSource
            from src.application.use_cases import CreateResearchQueryUseCase
            from src.infrastructure.scholarly_sources import UnifiedScholarlySearcher
            from src.presentation.mcp_server import McpServerHandler

            return {"status": "PASS", "message": "All core modules import successfully"}
        except ImportError as e:
            return {"status": "FAIL", "message": f"Import failed: {e}"}

    def check_domain_layer(self) -> Dict[str, str]:
        """Check domain layer functionality."""
        try:
            # Test entity creation
            query = ResearchQuery(
                id=QueryId(),
                text="test query",
                query_type=ResearchQueryType.ACADEMIC,
                created_at=datetime.now(),
                max_sources=5,
                include_academic_sources=True,
            )

            if query.text == "test query" and query.max_sources == 5:
                return {
                    "status": "PASS",
                    "message": "Domain entities working correctly",
                }
            else:
                return {"status": "FAIL", "message": "Domain entity validation failed"}

        except Exception as e:
            return {"status": "FAIL", "message": f"Domain layer error: {e}"}

    def check_application_layer(self) -> Dict[str, str]:
        """Check application layer use cases."""
        try:
            # Test use case initialization
            repo = InMemoryResearchQueryRepository()
            use_case = ScholarlyResearchUseCase(
                repo, InMemoryResearchResultRepository()
            )

            # Test citation export (without external API calls)
            sample_papers = [
                {
                    "title": "Test Paper",
                    "authors": ["Test Author"],
                    "year": 2024,
                    "venue": "Test Conference",
                    "abstract": "Test abstract",
                }
            ]

            bibtex = use_case.export_citations(sample_papers, "bibtex")

            if "@article{" in bibtex and "Test Paper" in bibtex:
                return {
                    "status": "PASS",
                    "message": "Application layer and citation export working",
                }
            else:
                return {
                    "status": "FAIL",
                    "message": "Citation export validation failed",
                }

        except Exception as e:
            return {"status": "FAIL", "message": f"Application layer error: {e}"}

    def check_infrastructure_layer(self) -> Dict[str, str]:
        """Check infrastructure components."""
        try:
            # Test repository functionality
            query_repo = InMemoryResearchQueryRepository()
            result_repo = InMemoryResearchResultRepository()

            # Test basic CRUD operations
            query = ResearchQuery(
                id=QueryId(),
                text="infrastructure test",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
                max_sources=3,
            )

            query_repo.save(query)
            retrieved = query_repo.find_by_id(query.id)

            if retrieved and retrieved.text == "infrastructure test":
                return {
                    "status": "PASS",
                    "message": "Infrastructure repositories working correctly",
                }
            else:
                return {"status": "FAIL", "message": "Repository functionality failed"}

        except Exception as e:
            return {"status": "FAIL", "message": f"Infrastructure error: {e}"}

    def check_web_interface(self) -> Dict[str, str]:
        """Check web interface functionality."""
        try:
            handler = WebInterfaceHandler()

            # Test API documentation generation
            docs = handler.get_api_documentation()

            if "openapi" in docs and "info" in docs:
                return {
                    "status": "PASS",
                    "message": "Web interface and API documentation working",
                }
            else:
                return {
                    "status": "FAIL",
                    "message": "API documentation generation failed",
                }

        except Exception as e:
            return {"status": "FAIL", "message": f"Web interface error: {e}"}

    def check_citation_export(self) -> Dict[str, str]:
        """Test citation export functionality in detail."""
        try:
            use_case = ScholarlyResearchUseCase(
                InMemoryResearchQueryRepository(), InMemoryResearchResultRepository()
            )

            test_paper = {
                "title": "Attention Is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
                "year": 2017,
                "venue": "NIPS",
                "doi": "10.5555/test",
                "abstract": "Test abstract for transformer paper",
            }

            # Test all export formats
            formats_results = {}
            for fmt in ["bibtex", "ris", "endnote", "apa"]:
                try:
                    export = use_case.export_citations([test_paper], fmt)
                    if export and len(export) > 10:  # Basic validation
                        formats_results[fmt] = "PASS"
                    else:
                        formats_results[fmt] = "FAIL"
                except Exception as e:
                    formats_results[fmt] = f"ERROR: {e}"

            passed_formats = sum(1 for v in formats_results.values() if v == "PASS")

            if passed_formats == 4:
                return {
                    "status": "PASS",
                    "message": f"All 4 citation formats working: {formats_results}",
                }
            elif passed_formats >= 2:
                return {
                    "status": "WARN",
                    "message": f"Some citation formats working: {formats_results}",
                }
            else:
                return {
                    "status": "FAIL",
                    "message": f"Citation export failed: {formats_results}",
                }

        except Exception as e:
            return {"status": "FAIL", "message": f"Citation export error: {e}"}

    def check_performance(self) -> Dict[str, str]:
        """Check basic performance metrics."""
        try:
            # Test query creation performance
            start_time = time.time()

            for i in range(100):
                query = ResearchQuery(
                    id=QueryId(),
                    text=f"performance test {i}",
                    query_type=ResearchQueryType.GENERAL,
                    created_at=datetime.now(),
                    max_sources=5,
                )

            duration = time.time() - start_time
            queries_per_second = 100 / duration

            if queries_per_second > 1000:
                return {
                    "status": "PASS",
                    "message": f"Performance excellent: {queries_per_second:.0f} queries/sec",
                }
            elif queries_per_second > 100:
                return {
                    "status": "WARN",
                    "message": f"Performance acceptable: {queries_per_second:.0f} queries/sec",
                }
            else:
                return {
                    "status": "FAIL",
                    "message": f"Performance poor: {queries_per_second:.0f} queries/sec",
                }

        except Exception as e:
            return {"status": "FAIL", "message": f"Performance test error: {e}"}

    def check_file_system(self) -> Dict[str, str]:
        """Check file system health and required directories."""
        try:
            required_paths = [
                "src/",
                "tests/",
                "docs/",
                "requirements.txt",
                "README.md",
            ]

            missing_paths = []
            for path in required_paths:
                if not Path(path).exists():
                    missing_paths.append(path)

            if not missing_paths:
                return {
                    "status": "PASS",
                    "message": "All required files and directories present",
                }
            else:
                return {"status": "WARN", "message": f"Missing paths: {missing_paths}"}

        except Exception as e:
            return {"status": "FAIL", "message": f"File system check error: {e}"}

    def check_git_status(self) -> Dict[str, str]:
        """Check git repository status."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                uncommitted = (
                    len(result.stdout.strip().split("\n"))
                    if result.stdout.strip()
                    else 0
                )

                # Get current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                branch = (
                    branch_result.stdout.strip()
                    if branch_result.returncode == 0
                    else "unknown"
                )

                if uncommitted == 0:
                    return {
                        "status": "PASS",
                        "message": f"Git repository clean on branch '{branch}'",
                    }
                else:
                    return {
                        "status": "WARN",
                        "message": f"Git repository has {uncommitted} uncommitted changes on branch '{branch}'",
                    }
            else:
                return {
                    "status": "WARN",
                    "message": "Not in a git repository or git not available",
                }

        except Exception as e:
            return {"status": "WARN", "message": f"Git status check failed: {e}"}


def main():
    """Run health checks and output results."""
    checker = HealthChecker()
    results = checker.run_all_checks()

    # Print summary
    print("\n" + "=" * 50)
    print("🏥 HEALTH CHECK SUMMARY")
    print("=" * 50)

    status_emoji = {"HEALTHY": "🟢", "WARNING": "🟡", "CRITICAL": "🔴"}

    overall_status = results["overall_status"]
    print(f"Overall Status: {status_emoji.get(overall_status, '⚪')} {overall_status}")
    print(
        f"Pass Rate: {results['pass_rate']:.1%} ({results['passed_checks']}/{results['total_checks']})"
    )
    print(f"Timestamp: {results['timestamp']}")

    # Save results to file
    output_file = Path("docs/health-check-results.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Exit with appropriate code
    if overall_status == "HEALTHY":
        print("\n✅ System is healthy and ready for production!")
        sys.exit(0)
    elif overall_status == "WARNING":
        print("\n⚠️  System has warnings but is generally functional")
        sys.exit(0)  # Don't fail CI/CD for warnings
    else:
        print("\n❌ System has critical issues that need attention")
        sys.exit(1)


if __name__ == "__main__":
    main()
