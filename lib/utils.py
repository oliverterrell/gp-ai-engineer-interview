import pandas as pd
from tabulate import tabulate


def load_data(data_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all CSV files."""
    messages_df = pd.read_csv(f"{data_dir}/messages.csv")
    products_df = pd.read_csv(f"{data_dir}/products.csv")
    history_df = pd.read_csv(f"{data_dir}/recommendations_history.csv")
    return messages_df, products_df, history_df


def print_dataframe(df: pd.DataFrame) -> None:
    """Pretty-print a dataframe."""
    print("\n", tabulate(df, headers=[c.upper() for c in df.columns], tablefmt='simple', showindex=False), "\n")
