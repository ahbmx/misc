from dvl import functionHelper, pandasHelper
from dvl.functionHelper import setup_logger, run_command
import pandas as pd

# Setup logger
logger = setup_logger('main')

# Example usage of command runner
stdout, stderr, retcode = run_command(
    "ls -la", 
    output_file="ls_output.txt",
    recreate=True,
    logger=logger
)

# Example usage of pandas functions
logger.info("Creating sample DataFrame")
data = {'A': range(10), 'B': [x**2 for x in range(10)]}
df = pd.DataFrame(data)

logger.info("Saving DataFrame to Parquet")
pandasHelper.save_to_parquet(df, "sample.parquet")

logger.info("Extended describe:")
print(pandasHelper.describe_extended(df))