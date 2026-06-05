import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2)
def compute_payroll_task(self, run_id: str):
    """Compute payroll for all employees in a payroll run."""
    logger.info(f"Computing payroll for run {run_id}")
    try:
        # TODO: Call payroll_service.compute_payroll(run_id)
        # This runs synchronously in Celery worker context
        # Need to create a sync DB session for this
        logger.info(f"Payroll computation completed for run {run_id}")
        return {"status": "completed", "run_id": run_id}
    except Exception as exc:
        logger.error(f"Payroll computation failed: {exc}")
        raise self.retry(exc=exc)
