import pandas as pd

left_data = ["Line 1", "Line 2", "Line 3"]
right_data = ["Right 1", "Right 2", "Right 3"]

df = pd.DataFrame({
    "Left Column": left_data,
    "Right Column": right_data
})

print(df.to_string(index=False, justify='left'))