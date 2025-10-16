"""
System Validation Script

Comprehensive validation of entire system before deployment.

Tests:
- Installation and dependencies
- Core functionality
- Integration tests
- Performance benchmarks
- Documentation completeness
"""

import sys
from pathlib import Path
import subprocess
import importlib
from typing import List, Tuple

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SystemValidator:
    """Validates system is ready for deployment."""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def run_check(self, name: str, check_func) -> bool:
        """Run a validation check."""
        print(f"\n{'='*80}")
        print(f"🔍 Checking: {name}")
        print(f"{'='*80}")
        
        try:
            check_func()
            print(f"✅ PASSED: {name}")
            self.results.append((name, True, None))
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {str(e)}")
            self.results.append((name, False, str(e)))
            self.failed += 1
            return False
    
    def validate_dependencies(self):
        """Check all required dependencies are installed."""
        print("\n📦 Validating Dependencies...")
        
        required_packages = [
            'numpy', 'pandas', 'scipy',
            'gymnasium', 'torch', 'stable_baselines3',
            'matplotlib', 'plotly', 'streamlit',
            'pytest', 'pyyaml'
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
                print(f"  ✓ {package}")
            except ImportError:
                raise ImportError(f"Missing required package: {package}")
        
        print("✅ All dependencies installed")
    
    def validate_project_structure(self):
        """Validate project directory structure."""
        print("\n📁 Validating Project Structure...")
        
        required_paths = [
            'src/simulation/order_book.py',
            'src/simulation/order_flow.py',
            'src/simulation/market_simulator.py',
            'src/impact/impact_models.py',
            'src/environments/market_making_env.py',
            'src/agents/baseline_agents.py',
            'src/agents/ppo_agent.py',
            'src/evaluation/metrics.py',
            'src/evaluation/backtester.py',
            'src/visualization/dashboard.py',
            'src/visualization/advanced_dashboard.py',
            'scripts/train.py',
            'scripts/evaluate.py',
            'tests/test_order_book.py',
            'tests/test_impact_models.py',
            'tests/test_environment.py',
            'tests/test_integration.py',
            'requirements.txt',
            'README.md',
            'Dockerfile',
            'docker-compose.yml'
        ]
        
        missing = []
        for path in required_paths:
            full_path = project_root / path
            if not full_path.exists():
                missing.append(path)
            else:
                print(f"  ✓ {path}")
        
        if missing:
            raise FileNotFoundError(f"Missing files: {', '.join(missing)}")
        
        print("✅ Project structure valid")
    
    def validate_imports(self):
        """Test that all modules can be imported."""
        print("\n📥 Validating Module Imports...")
        
        modules = [
            'src.simulation.order_book',
            'src.simulation.order_flow',
            'src.simulation.market_simulator',
            'src.impact.impact_models',
            'src.environments.market_making_env',
            'src.agents.baseline_agents',
            'src.agents.ppo_agent',
            'src.evaluation.metrics',
            'src.evaluation.backtester'
        ]
        
        for module in modules:
            importlib.import_module(module)
            print(f"  ✓ {module}")
        
        print("✅ All modules importable")
    
    def validate_core_functionality(self):
        """Test core system functionality."""
        print("\n⚙️ Validating Core Functionality...")
        
        from src.simulation.order_book import LimitOrderBook, Order, OrderType, OrderSide
        from src.environments.market_making_env import MarketMakingEnv
        from src.agents.baseline_agents import StaticSpreadAgent
        
        # Test LOB
        print("  Testing LOB...")
        lob = LimitOrderBook(tick_size=0.01)
        order = Order(1, OrderSide.BUY, OrderType.LIMIT, 100.0, 100, 0.0)
        lob.submit_order(order)
        assert lob.get_best_bid() == 100.0
        print("    ✓ LOB working")
        
        # Test Environment
        print("  Testing Environment...")
        env = MarketMakingEnv()
        obs, _ = env.reset(seed=42)
        assert obs.shape == (9,)
        print("    ✓ Environment working")
        
        # Test Agent
        print("  Testing Agent...")
        agent = StaticSpreadAgent()
        action = agent.get_action(obs)
        assert action.shape == (4,)
        print("    ✓ Agent working")
        
        print("✅ Core functionality validated")
    
    def validate_integration_tests(self):
        """Run integration test suite."""
        print("\n🧪 Running Integration Tests...")
        
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/test_integration.py', '-v'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            raise RuntimeError("Integration tests failed")
        
        print("✅ Integration tests passed")
    
    def validate_documentation(self):
        """Check documentation completeness."""
        print("\n📚 Validating Documentation...")
        
        doc_files = [
            'README.md',
            'docs/USER_GUIDE.md',
            'docs/TECHNICAL_OVERVIEW.md',
            'docs/RESEARCH_PAPER_TEMPLATE.md',
            'deploy/deployment_guide.md'
        ]
        
        for doc in doc_files:
            path = project_root / doc
            if not path.exists():
                raise FileNotFoundError(f"Missing documentation: {doc}")
            
            # Check file is not empty
            if path.stat().st_size < 100:
                raise ValueError(f"Documentation too short: {doc}")
            
            print(f"  ✓ {doc}")
        
        print("✅ Documentation complete")
    
    def validate_configuration(self):
        """Validate configuration files."""
        print("\n⚙️ Validating Configuration Files...")
        
        import yaml
        
        configs = [
            'experiments/configs/ppo_baseline.yaml',
            'experiments/configs/ppo_aggressive.yaml'
        ]
        
        for config in configs:
            path = project_root / config
            if not path.exists():
                raise FileNotFoundError(f"Missing config: {config}")
            
            # Validate YAML syntax
            with open(path) as f:
                data = yaml.safe_load(f)
                assert isinstance(data, dict)
            
            print(f"  ✓ {config}")
        
        print("✅ Configurations valid")
    
    def validate_deployment_readiness(self):
        """Check deployment infrastructure."""
        print("\n🚀 Validating Deployment Readiness...")
        
        # Check Docker files
        docker_files = ['Dockerfile', 'docker-compose.yml', '.dockerignore']
        for file in docker_files:
            if not (project_root / file).exists():
                raise FileNotFoundError(f"Missing Docker file: {file}")
            print(f"  ✓ {file}")
        
        # Check deployment guide
        deployment_guide = project_root / 'deploy/deployment_guide.md'
        if not deployment_guide.exists():
            raise FileNotFoundError("Missing deployment guide")
        print("  ✓ deployment_guide.md")
        
        print("✅ Deployment ready")
    
    def performance_benchmark(self):
        """Run performance benchmarks."""
        print("\n⚡ Running Performance Benchmarks...")
        
        import time
        from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
        from src.agents.baseline_agents import StaticSpreadAgent
        
        env = MarketMakingEnv(MarketMakingConfig(episode_duration=10.0))
        agent = StaticSpreadAgent()
        
        # Benchmark episode execution time
        start = time.time()
        obs, _ = env.reset(seed=42)
        
        for _ in range(10):
            action = agent.get_action(obs)
            obs, reward, term, trunc, info = env.step(action)
            if term or trunc:
                break
        
        elapsed = time.time() - start
        steps_per_second = 10 / elapsed
        
        print(f"  Performance: {steps_per_second:.1f} steps/second")
        
        if steps_per_second < 10:
            raise RuntimeError(f"Performance too slow: {steps_per_second:.1f} steps/s")
        
        print("✅ Performance acceptable")
    
    def generate_report(self):
        """Generate validation report."""
        print("\n" + "="*80)
        print("VALIDATION REPORT")
        print("="*80)
        print(f"\nTotal Checks: {self.passed + self.failed}")
        print(f"Passed: {self.passed} ({100*self.passed/(self.passed+self.failed):.1f}%)")
        print(f"Failed: {self.failed}")
        
        if self.failed > 0:
            print("\n❌ Failed Checks:")
            for name, passed, error in self.results:
                if not passed:
                    print(f"  - {name}: {error}")
        
        print("\n" + "="*80)
        
        if self.failed == 0:
            print("\n✅ ✅ ✅  SYSTEM VALIDATED - READY FOR DEPLOYMENT  ✅ ✅ ✅\n")
            return True
        else:
            print("\n❌ VALIDATION FAILED - FIX ISSUES BEFORE DEPLOYMENT\n")
            return False


def main():
    """Run full system validation."""
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  SYSTEM VALIDATION - DEPLOYMENT READINESS CHECK".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝\n")
    
    validator = SystemValidator()
    
    # Run all validation checks
    checks = [
        ("Dependencies", validator.validate_dependencies),
        ("Project Structure", validator.validate_project_structure),
        ("Module Imports", validator.validate_imports),
        ("Core Functionality", validator.validate_core_functionality),
        ("Integration Tests", validator.validate_integration_tests),
        ("Documentation", validator.validate_documentation),
        ("Configuration Files", validator.validate_configuration),
        ("Deployment Infrastructure", validator.validate_deployment_readiness),
        ("Performance Benchmarks", validator.performance_benchmark)
    ]
    
    for name, check_func in checks:
        validator.run_check(name, check_func)
    
    # Generate report
    success = validator.generate_report()
    
    # Save report
    report_path = project_root / "VALIDATION_REPORT.txt"
    with open(report_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("SYSTEM VALIDATION REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date: {Path(__file__).stat().st_mtime}\n")
        f.write(f"Total Checks: {validator.passed + validator.failed}\n")
        f.write(f"Passed: {validator.passed}\n")
        f.write(f"Failed: {validator.failed}\n\n")
        
        for name, passed, error in validator.results:
            status = "✅ PASS" if passed else "❌ FAIL"
            f.write(f"{status}: {name}\n")
            if error:
                f.write(f"  Error: {error}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("VALIDATION " + ("PASSED" if success else "FAILED") + "\n")
        f.write("="*80 + "\n")
    
    print(f"\n📄 Report saved to: {report_path}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
