#!/usr/bin/env python3
"""
Analyze recommendation quality against actual purchases.

Usage:
    python analyze.py                                    # Analyze historical recommendations
    python analyze.py -r recommendations.csv             # Analyze your new recommendations
    python analyze.py -r recommendations.csv --compare   # Compare new vs historical
"""

import argparse
import pandas as pd

from lib import Analyzer, load_data


def main():
    parser = argparse.ArgumentParser(description="Analyze recommendation accuracy")
    parser.add_argument(
        "-r", "--recommendations",
        type=str,
        help="Path to recommendations CSV (default: historical)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare provided recommendations against historical"
    )
    parser.add_argument(
        "-d", "--data-dir",
        default="data",
        help="Data directory path"
    )
    args = parser.parse_args()

    # Load base data
    messages_df, products_df, history_df = load_data(args.data_dir)
    analyzer = Analyzer()

    if args.compare and args.recommendations:
        # Compare mode: show both historical and new
        new_recs_df = pd.read_csv(args.recommendations)

        historical_result = analyzer.analyze(messages_df, products_df, history_df)
        new_result = analyzer.analyze(messages_df, products_df, new_recs_df)

        print(analyzer.format_results(historical_result, "Historical Recommendations"))
        print(analyzer.format_results(new_result, "New Recommendations"))

        # Print comparison summary
        print("=" * 50)
        print(" COMPARISON SUMMARY")
        print("=" * 50)
        print(f"  Exact Match:    {historical_result.exact_match_rate:>6.1%} → {new_result.exact_match_rate:>6.1%}  ({'+' if new_result.exact_match_rate > historical_result.exact_match_rate else ''}{(new_result.exact_match_rate - historical_result.exact_match_rate)*100:+.1f}pp)")
        print(f"  Category Match: {historical_result.category_match_rate:>6.1%} → {new_result.category_match_rate:>6.1%}  ({'+' if new_result.category_match_rate > historical_result.category_match_rate else ''}{(new_result.category_match_rate - historical_result.category_match_rate)*100:+.1f}pp)")
        print(f"  Out-of-Stock:   {historical_result.out_of_stock_rate:>6.1%} → {new_result.out_of_stock_rate:>6.1%}  ({'+' if new_result.out_of_stock_rate < historical_result.out_of_stock_rate else ''}{(historical_result.out_of_stock_rate - new_result.out_of_stock_rate)*100:+.1f}pp)")
        print()

    elif args.recommendations:
        # Analyze provided recommendations only
        recs_df = pd.read_csv(args.recommendations)
        result = analyzer.analyze(messages_df, products_df, recs_df)
        print(analyzer.format_results(result, f"Analysis: {args.recommendations}"))

    else:
        # Default: analyze historical
        result = analyzer.analyze(messages_df, products_df, history_df)
        print(analyzer.format_results(result, "Historical Recommendations"))


if __name__ == "__main__":
    main()
