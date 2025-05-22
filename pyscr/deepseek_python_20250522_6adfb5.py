import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from . import LOG_PATH, LOG_LEVEL, LOG_FILE, OUTPUT_PATH

def setup_logger(name: str = __name__, log_level: Optional[str] = None) -> logging.Logger:
    """Setup logger that outputs to both console and file."""
    log_level = log_level or LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler
    log_file = Path(LOG_PATH) / LOG_FILE
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger

def run_command(
    command: str, 
    output_file: Optional[str] = None, 
    recreate: bool = False,
    logger: Optional[logging.Logger] = None
) -> Tuple[str, str, int]:
    """
    Run a command and optionally store output to file.
    
    Args:
        command: Command to run
        output_file: File to store output (relative to OUTPUT_PATH)
        recreate: If True, recreate the output file if it exists
        logger: Optional logger instance
        
    Returns:
        Tuple of (stdout, stderr, returncode)
    """
    if logger is None:
        logger = setup_logger()
    
    if output_file:
        output_path = Path(OUTPUT_PATH) / output_file
        if output_path.exists() and not recreate:
            logger.info(f"Output file {output_path} exists, skipping command execution")
            with open(output_path, 'r') as f:
                content = f.read()
            return content, "", 0
    
    logger.info(f"Executing command: {command}")
    result = subprocess.run(
        command, 
        shell=True, 
        text=True, 
        capture_output=True,
        timeout=DEFAULT_TIMEOUT
    )
    
    if output_file:
        with open(output_path, 'w') as f:
            f.write(result.stdout)
        logger.info(f"Command output saved to {output_path}")
    
    return result.stdout, result.stderr, result.returncode