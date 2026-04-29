"""
evaluation_service.py - DEPRECATED

This module previously contained:
- evaluate_answer() - REPLACED by evaluator_agent() in app/agents/evaluator.py
- generate_final_feedback() - REPLACED by reporter_agent() in app/agents/reporter.py

These functions are no longer used. The Celery task orchestrator (app/agents/tasks.py)
now uses the specialized agent functions from the agents module.

See:
- app/agents/evaluator.py for answer scoring
- app/agents/reporter.py for final interview reports
"""