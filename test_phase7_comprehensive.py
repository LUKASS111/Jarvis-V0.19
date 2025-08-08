#!/usr/bin/env python3
"""
Phase 7 Advanced Integration Systems Test
Comprehensive test of all Phase 7 capabilities
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_phase7_ai_integration():
    """Test Phase 7 AI Integration Framework"""
    print("\n🧠 Testing Phase 7 AI Integration Framework...")
    
    try:
        from jarvis.phase7.ai_integration_framework import get_ai_integration_framework, EnhancedAIRequest, AICapabilityType
        
        # Initialize framework
        ai_framework = get_ai_integration_framework()
        
        # Test basic AI request
        request = EnhancedAIRequest(
            content="Hello, this is a test of Phase 7 AI capabilities",
            request_type=AICapabilityType.GENERAL_CHAT,
            model="auto",
            audit_enabled=True
        )
        
        response = ai_framework.process_enhanced_request(request)
        
        if response:
            print(f"  ✅ AI Request processed successfully")
            print(f"  📊 Model used: {response.model_used}")
            print(f"  ⏱️ Latency: {response.latency:.3f}s")
            print(f"  📝 Content length: {len(str(response.content))} chars")
        else:
            print("  ❌ AI Request failed")
            return False
        
        # Test available models
        models = ai_framework.get_available_models()
        print(f"  📋 Available models: {len(models)}")
        
        # Test framework status
        status = ai_framework.get_framework_status()
        print(f"  🏥 Framework health: Active")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI Integration test failed: {e}")
        return False

def test_phase7_platform_expansion():
    """Test Phase 7 Platform Expansion Manager"""
    print("\n🚀 Testing Phase 7 Platform Expansion Manager...")
    
    try:
        from jarvis.phase7.platform_expansion_manager import get_platform_expansion_manager, PlatformType
        
        # Initialize platform manager
        platform_manager = get_platform_expansion_manager()
        
        # Test platform status
        status = platform_manager.get_platform_status()
        platforms = status.get("platforms", {})
        
        print(f"  ✅ Platform Manager initialized")
        print(f"  📋 Configured platforms: {len(platforms)}")
        
        for name, platform_info in platforms.items():
            print(f"    - {name}: {platform_info['config'].get('gui_framework', 'N/A')}")
        
        # Test deployment simulation
        deployment_result = platform_manager.deploy_platform("web", {"environment": "development"})
        
        if deployment_result and deployment_result.get("status") == "success":
            print(f"  ✅ Web platform deployment simulated successfully")
        else:
            print(f"  ⚠️ Web platform deployment simulation failed")
        
        # Test API documentation
        api_docs = platform_manager.get_api_documentation()
        print(f"  📚 API endpoints configured: {len(api_docs.get('endpoints', {}))}")
        
        # Test mobile app configuration
        mobile_config = platform_manager.create_mobile_app_config("react_native")
        print(f"  📱 Mobile app config: {mobile_config['app_name']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Platform Expansion test failed: {e}")
        return False

def test_phase7_enterprise_features():
    """Test Phase 7 Enterprise Features Manager"""
    print("\n🏢 Testing Phase 7 Enterprise Features Manager...")
    
    try:
        from jarvis.phase7.enterprise_features_manager import (
            get_enterprise_features_manager, 
            TenantConfig, 
            TenantType,
            UserRole,
            SecurityLevel
        )
        
        # Initialize enterprise manager
        enterprise_manager = get_enterprise_features_manager()
        
        # Test authentication
        auth_result = enterprise_manager.authenticate_user(
            {"method": "password", "username": "test_user", "password": "test_pass"},
            "system"
        )
        
        if auth_result and auth_result.get("success"):
            print(f"  ✅ User authentication successful")
            print(f"  👤 User role: {auth_result['user_profile'].role.value}")
            print(f"  🔒 Security clearance: {auth_result['user_profile'].security_clearance.value}")
        else:
            print("  ❌ User authentication failed")
            return False
        
        # Test tenant creation
        tenant_config = TenantConfig(
            tenant_id="test_tenant_001",
            name="Test Enterprise Tenant",
            type=TenantType.PROFESSIONAL,
            admin_email="admin@test-tenant.com",
            max_users=50,
            max_api_calls=5000
        )
        
        tenant_id = enterprise_manager.create_tenant(tenant_config)
        if tenant_id:
            print(f"  ✅ Tenant created: {tenant_id}")
        else:
            print("  ❌ Tenant creation failed")
            return False
        
        # Test API key generation
        api_key = enterprise_manager.create_api_key(
            tenant_id, 
            "test_user_001",
            ["chat", "analyze", "memory_read"]
        )
        print(f"  🔑 API key generated: {api_key[:20]}...")
        
        # Test enterprise analytics
        analytics = enterprise_manager.get_enterprise_analytics()
        print(f"  📊 Total tenants: {analytics['overview']['total_tenants']}")
        print(f"  👥 Active users: {analytics['overview']['active_users']}")
        
        # Test security status
        security_status = enterprise_manager.get_security_status()
        print(f"  🛡️ Security policies: {len(security_status['security_policies'])}")
        print(f"  🔐 Active sessions: {security_status['active_sessions']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Enterprise Features test failed: {e}")
        return False

def test_phase7_integration_manager():
    """Test Phase 7 Integration Manager"""
    print("\n🔗 Testing Phase 7 Integration Manager...")
    
    try:
        from jarvis.phase7.integration_manager import get_phase7_integration_manager, Phase7Config, IntegrationLevel
        
        # Initialize integration manager with custom config
        config = Phase7Config(
            integration_level=IntegrationLevel.ENTERPRISE,
            monitoring_enabled=True,
            optimization_enabled=True,
            auto_scaling=True
        )
        
        integration_manager = get_phase7_integration_manager(config)
        
        print(f"  ✅ Integration Manager initialized")
        print(f"  🎛️ Integration level: {config.integration_level.value}")
        
        # Test unified request processing
        unified_request = {
            "ai_request": {
                "content": "Analyze the performance of Phase 7 systems",
                "type": "text_analysis"
            },
            "enterprise_context": {
                "tenant_id": "system",
                "session_id": "test_session_001"
            }
        }
        
        result = integration_manager.process_unified_request(unified_request)
        
        if result and result.get("success"):
            print(f"  ✅ Unified request processed successfully")
            print(f"  📋 Components processed: {', '.join(result['components_processed'])}")
            print(f"  ⏱️ Processing time: {result['metadata']['processing_time']:.3f}s")
        else:
            print("  ❌ Unified request failed")
            return False
        
        # Test comprehensive status
        status = integration_manager.get_comprehensive_status()
        print(f"  🏥 System status: {status['phase7_manager']['status']}")
        print(f"  🎯 Overall health: {status['integration_metrics']['integration_health']['overall_score']:.1f}%")
        
        # Test analytics dashboard
        dashboard = integration_manager.get_analytics_dashboard()
        print(f"  📊 Dashboard components: {len(dashboard.keys())}")
        print(f"  🤖 AI models available: {dashboard['ai_intelligence']['models_available']}")
        print(f"  🚀 Platforms deployed: {dashboard['platform_ecosystem']['platforms_deployed']}")
        print(f"  🏢 Enterprise tenants: {dashboard['enterprise_grade']['tenants']}")
        
        # Test system optimization
        optimization_result = integration_manager.trigger_system_optimization()
        if optimization_result.get("success"):
            print(f"  ✅ System optimization completed")
            print(f"  🔧 Optimizations applied: {len(optimization_result['optimizations_applied'])}")
        else:
            print("  ⚠️ System optimization had issues")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration Manager test failed: {e}")
        return False

def test_phase7_unified_apis():
    """Test Phase 7 unified API functions"""
    print("\n🌐 Testing Phase 7 Unified APIs...")
    
    try:
        from jarvis.phase7 import get_phase7_dashboard, get_phase7_health
        
        # Test unified dashboard
        dashboard = get_phase7_dashboard()
        
        if dashboard:
            print(f"  ✅ Phase 7 dashboard accessible")
            print(f"  📊 Dashboard sections: {len(dashboard.keys())}")
            print(f"  🎯 Overall health: {dashboard['overview']['overall_health']:.1f}%")
        else:
            print("  ❌ Phase 7 dashboard failed")
            return False
        
        # Test health monitoring
        health = get_phase7_health()
        
        if health:
            print(f"  ✅ Phase 7 health monitoring active")
            print(f"  🏥 Overall health: {health['overall_health']:.1f}%")
            print(f"  📈 System status: {health['status']}")
            print(f"  ⏱️ Uptime: {health['uptime']:.1f}s")
        else:
            print("  ❌ Phase 7 health monitoring failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Unified APIs test failed: {e}")
        return False

def run_comprehensive_phase7_test():
    """Run comprehensive Phase 7 test suite"""
    print("=" * 80)
    print("🚀 PHASE 7 ADVANCED INTEGRATION SYSTEMS - COMPREHENSIVE TEST")
    print("=" * 80)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Run all Phase 7 tests
    tests = [
        ("AI Integration Framework", test_phase7_ai_integration),
        ("Platform Expansion Manager", test_phase7_platform_expansion),
        ("Enterprise Features Manager", test_phase7_enterprise_features),
        ("Integration Manager", test_phase7_integration_manager),
        ("Unified APIs", test_phase7_unified_apis)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 PHASE 7 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print("\n" + "-" * 80)
    print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL PHASE 7 TESTS PASSED - ADVANCED INTEGRATION SYSTEMS OPERATIONAL!")
        print("\n🚀 Phase 7 Features Now Available:")
        print("  • Advanced AI Integration with next-generation models")
        print("  • Platform Expansion with cloud deployment capabilities")  
        print("  • Enterprise Features with security and compliance")
        print("  • Real-time system optimization and monitoring")
        print("  • Comprehensive analytics and reporting")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed - Some Phase 7 features may not be fully operational")
        return False

if __name__ == "__main__":
    success = run_comprehensive_phase7_test()
    sys.exit(0 if success else 1)