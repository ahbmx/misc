from tabulate import tabulate

data = [
    ["Left item 1", "Right item 1"],
    ["Left item 2", "Right item 2"],
    ["Left item 3", "Right item 3"],
]

print(tabulate(data, tablefmt="plain"))