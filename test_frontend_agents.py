"""Test frontend parallel agents with 3 scenarios."""

import asyncio
import json
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_frontend_orchestrator():
    """Test frontend orchestrator with 3 project types."""
    
    test_cases = [
        {
            "name": "📝 Simple Todo App",
            "validation": {
                "status": "success",
                "project_type": "CRUD backend",
                "complexity": "beginner",
                "user_stack": {
                    "backend": "Express.js",
                    "frontend": "React",
                    "database": "MongoDB",
                    "deployment": "Heroku",
                    "realtime": "No"
                },
                "feedback": "Simple todo application with basic CRUD operations",
                "missing_requirements": [],
                "alignment_score": 90
            }
        },
        {
            "name": "💬 Real-time Chat App",
            "validation": {
                "status": "success",
                "project_type": "real-time",
                "complexity": "advanced",
                "user_stack": {
                    "backend": "FastAPI",
                    "frontend": "Next.js",
                    "database": "PostgreSQL",
                    "deployment": "AWS",
                    "realtime": "Yes"
                },
                "feedback": "Real-time chat application with WebSocket support",
                "missing_requirements": [],
                "alignment_score": 85
            }
        },
        {
            "name": "🤖 AI System",
            "validation": {
                "status": "success",
                "project_type": "AI system",
                "complexity": "advanced",
                "user_stack": {
                    "backend": "FastAPI",
                    "frontend": "React",
                    "database": "PostgreSQL",
                    "deployment": "GCP",
                    "realtime": "Yes"
                },
                "feedback": "AI-powered system with prompt engineering and result caching",
                "missing_requirements": [],
                "alignment_score": 88
            }
        }
    ]
    
    logger.info("\n" + "=" * 70)
    logger.info("🎨 FRONTEND PARALLEL AGENTS TEST SUITE")
    logger.info("=" * 70)
    
    for test_case in test_cases:
        logger.info(f"\n🧪 Testing: {test_case['name']}")
        logger.info("-" * 70)
        
        try:
            # Import here to avoid circular imports
            from frontend_orchestrator import orchestrate_frontend_planning
            
            start_time = time.time()
            result = await orchestrate_frontend_planning(test_case["validation"])
            elapsed = time.time() - start_time
            
            if result.get("status") == "success":
                logger.info(f"✅ Success in {elapsed:.1f}s")
                logger.info(f"   Framework: {result['frontend_architecture']['framework']}")
                logger.info(f"   Styling: {result['frontend_architecture']['styling']}")
                logger.info(f"   Components: {result['total_components']}")
                logger.info(f"   Routes: {result['total_routes']}")
                logger.info(f"   Accessibility: {result['accessibility']['wcag_level']}")
            else:
                logger.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Test error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_frontend_orchestrator())
