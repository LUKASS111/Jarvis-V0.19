#!/usr/bin/env python3
"""
Comprehensive Stage Validation Summary
Executes all stage validations and provides summary report
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

class ComprehensiveValidator:
    def __init__(self):
        self.results = {
            "validation_timestamp": datetime.now().isoformat(),
            "stages": {},
            "overall_summary": {
                "total_stages": 5,
                "stages_passed": 0,
                "stages_partial": 0,
                "stages_failed": 0,
                "critical_issues": [],
                "readiness_for_stage6": False
            }
        }
    
    def run_stage_validation(self, stage_num):
        """Run validation for a specific stage"""
        script_path = f"scripts/validate_stage{stage_num}_completion.py"
        
        if not Path(script_path).exists():
            return {
                "status": "FAIL", 
                "error": f"Validation script not found: {script_path}"
            }
        
        try:
            result = subprocess.run(['python', script_path], 
                                  capture_output=True, text=True, timeout=60)
            
            # Determine status from exit code and output
            if result.returncode == 0:
                if "Overall Status: PASS" in result.stdout:
                    status = "PASS"
                else:
                    status = "PARTIAL"
            else:
                if "Overall Status: PARTIAL" in result.stdout:
                    status = "PARTIAL"
                else:
                    status = "FAIL"
            
            return {
                "status": status,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "error": "Validation timeout"}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def analyze_critical_issues(self):
        """Analyze critical issues across all stages"""
        critical_issues = []
        
        # Check Stage 1 - Legacy elimination
        stage1 = self.results["stages"].get("1", {})
        if stage1.get("status") != "PASS":
            critical_issues.append("Stage 1: Legacy code elimination incomplete - blocks Stage 6 execution")
        
        # Check Stage 5 - GUI implementation
        stage5 = self.results["stages"].get("5", {})
        if stage5.get("status") != "PASS":
            critical_issues.append("Stage 5: GUI implementation gaps - affects user experience guarantee")
        
        # Check for missing validation scripts
        required_scripts = [
            "validate_stage1_completion.py",
            "validate_stage2_completion.py", 
            "validate_stage3_completion.py",
            "validate_stage4_completion.py",
            "validate_stage5_completion.py"
        ]
        
        missing_scripts = []
        for script in required_scripts:
            if not Path(f"scripts/{script}").exists():
                missing_scripts.append(script)
        
        if missing_scripts:
            critical_issues.append(f"Missing validation scripts: {', '.join(missing_scripts)}")
        
        return critical_issues
    
    def determine_stage6_readiness(self):
        """Determine if system is ready for Stage 6"""
        # Stage 6 readiness criteria:
        # 1. All previous stages should be PASS or acceptable PARTIAL
        # 2. No critical blocking issues
        # 3. Core system operational
        
        stages_status = [self.results["stages"].get(str(i), {}).get("status", "FAIL") for i in range(1, 6)]
        
        # Allow some PARTIAL but no FAIL
        failed_stages = stages_status.count("FAIL")
        passed_stages = stages_status.count("PASS")
        
        # Check core system
        core_system_ok = True
        try:
            result = subprocess.run(['python', 'main.py', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            core_system_ok = result.returncode == 0 and "Jarvis" in result.stdout
        except:
            core_system_ok = False
        
        readiness = (
            failed_stages == 0 and  # No failed stages
            passed_stages >= 3 and  # At least 3 stages passed
            core_system_ok and      # Core system working
            len(self.results["overall_summary"]["critical_issues"]) <= 2  # Manageable issues
        )
        
        return readiness
    
    def run_comprehensive_validation(self):
        """Run validation for all stages"""
        print("🔍 COMPREHENSIVE STAGE VALIDATION")
        print("=" * 50)
        print("Executing validation for Stages 1-5...")
        print()
        
        for stage_num in range(1, 6):
            print(f"📋 Validating Stage {stage_num}...")
            stage_result = self.run_stage_validation(stage_num)
            self.results["stages"][str(stage_num)] = stage_result
            
            status_emoji = "✅" if stage_result["status"] == "PASS" else "⚠️" if stage_result["status"] == "PARTIAL" else "❌"
            print(f"{status_emoji} Stage {stage_num}: {stage_result['status']}")
        
        # Analyze results
        print("\n🔍 Analyzing results...")
        
        # Count stage statuses
        for stage_data in self.results["stages"].values():
            status = stage_data.get("status", "FAIL")
            if status == "PASS":
                self.results["overall_summary"]["stages_passed"] += 1
            elif status == "PARTIAL":
                self.results["overall_summary"]["stages_partial"] += 1
            else:
                self.results["overall_summary"]["stages_failed"] += 1
        
        # Analyze critical issues
        self.results["overall_summary"]["critical_issues"] = self.analyze_critical_issues()
        
        # Determine Stage 6 readiness
        self.results["overall_summary"]["readiness_for_stage6"] = self.determine_stage6_readiness()
        
        return self.results
    
    def print_summary(self):
        """Print comprehensive validation summary"""
        summary = self.results["overall_summary"]
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"🕐 Validation Time: {self.results['validation_timestamp']}")
        print(f"📈 Stages Status:")
        print(f"   ✅ Passed: {summary['stages_passed']}")
        print(f"   ⚠️  Partial: {summary['stages_partial']}")
        print(f"   ❌ Failed: {summary['stages_failed']}")
        print()
        
        # Stage details
        print("📋 STAGE-BY-STAGE RESULTS:")
        for stage_num in range(1, 6):
            stage_data = self.results["stages"].get(str(stage_num), {})
            status = stage_data.get("status", "MISSING")
            status_emoji = "✅" if status == "PASS" else "⚠️" if status == "PARTIAL" else "❌"
            print(f"   {status_emoji} Stage {stage_num}: {status}")
        print()
        
        # Critical issues
        if summary["critical_issues"]:
            print("🚨 CRITICAL ISSUES:")
            for issue in summary["critical_issues"]:
                print(f"   - {issue}")
            print()
        
        # Stage 6 readiness
        readiness_emoji = "✅" if summary["readiness_for_stage6"] else "❌"
        print(f"{readiness_emoji} STAGE 6 READINESS: {'READY' if summary['readiness_for_stage6'] else 'NOT READY'}")
        
        if not summary["readiness_for_stage6"]:
            print("\n💡 REQUIRED ACTIONS BEFORE STAGE 6:")
            if summary["stages_failed"] > 0:
                print("   - Fix failed stage validations")
            if len(summary["critical_issues"]) > 2:
                print("   - Address critical issues")
            print("   - Complete foundation repair as identified in validation results")
        else:
            print("\n🎯 READY TO PROCEED: Stage 6 execution can begin")
        
        print("\n" + "=" * 60)

def main():
    validator = ComprehensiveValidator()
    results = validator.run_comprehensive_validation()
    validator.print_summary()
    
    # Save comprehensive report
    output_file = f"comprehensive_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Comprehensive report saved: {output_file}")
    
    # Return exit code based on readiness
    return 0 if results["overall_summary"]["readiness_for_stage6"] else 1

if __name__ == "__main__":
    exit(main())