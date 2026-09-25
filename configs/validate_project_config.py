import sys
import logging
import importlib.util


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def read_validate_config(path):
    spec = importlib.util.spec_from_file_location("config", path)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    if not cfg.PROJECT_DIR:
        logger.error(f"Project directory is not specified")
        sys.exit(1)
    if not cfg.BUFFER_DIR:
        logger.error(f"Input directory is not specified")
        sys.exit(1)
    if not cfg.STATS_DIR:
        logger.error(f"Output directory is not specified")
        sys.exit(1)
    if not cfg.START_TIME:
        logger.error(f"Start time is not specified")
        sys.exit(1)
    if not cfg.END_TIME:
        logger.error(f"End time is not specified")
        sys.exit(1)
    if not cfg.VP_LIST:
        logger.error(f"No viewpoint specified.")
        sys.exit(1)
    for vp in cfg.VP_LIST:
        if not vp.get("country"):
            logger.error(f"Viewpoint country is not specified.")
            sys.exit(1)
        if vp.get("probe_id", None) and not vp.get("airport", None):
            logger.debug(f"Viewpoint probe ID is specified but no airport provided.")
            sys.exit(1)
    
    return cfg