"""
Analyzer for comparing recommendations against actual purchases.

Compares any recommendation set against ground truth (messages.converted_to_purchase)
to measure accuracy, relevance, and quality metrics.
"""
import pandas as pd

from dataclasses import dataclass
from pandas import DataFrame


@dataclass
class AnalysisResult:
    """Results from analyzing a recommendation set."""
    # Core accuracy metrics
    total_messages: int
    messages_with_purchase: int
    recommendations_made: int
    exact_matches: int
    category_matches: int

    # Quality metrics
    out_of_stock_recommendations: int
    avg_recommended_rating: float
    avg_confidence: float | None  # Only for new recommendations with confidence scores

    # Derived metrics
    @property
    def exact_match_rate(self) -> float:
        """% of purchasers who got the exact right recommendation."""
        return self.exact_matches / self.messages_with_purchase if self.messages_with_purchase > 0 else 0.0

    @property
    def category_match_rate(self) -> float:
        """% of purchasers who got a recommendation in the right category."""
        return self.category_matches / self.messages_with_purchase if self.messages_with_purchase > 0 else 0.0

    @property
    def out_of_stock_rate(self) -> float:
        """% of recommendations for out-of-stock products."""
        return self.out_of_stock_recommendations / self.recommendations_made if self.recommendations_made > 0 else 0.0

    @property
    def recommendation_coverage(self) -> float:
        """% of purchase-intent messages that got a recommendation."""
        return self.recommendations_made / self.messages_with_purchase if self.messages_with_purchase > 0 else 0.0


class Analyzer:
    """Analyzes recommendation quality against ground truth."""

    def analyze(
            self,
            messages_df: DataFrame,
            products_df: DataFrame,
            recommendations_df: DataFrame,
    ) -> AnalysisResult:
        """
        Analyze recommendations against actual purchases.
        
        Args:
            messages_df: Must have 'message_id', 'converted_to_purchase'
            products_df: Must have 'product_id', 'category', 'stock_quantity', 'avg_rating'
            recommendations_df: Must have 'message_id', 'recommended_product_id'
                               Optionally has 'confidence'
        """
        # Build lookup for product categories
        product_categories = products_df.set_index('product_id')['category'].to_dict()
        product_stock = products_df.set_index('product_id')['stock_quantity'].to_dict()
        product_ratings = products_df.set_index('product_id')['avg_rating'].to_dict()

        # Get messages that had actual purchases (ground truth)
        messages_with_purchase = messages_df[
            messages_df['converted_to_purchase'].notna() &
            (messages_df['converted_to_purchase'] != '')
            ].copy()

        # Merge recommendations with messages
        # Use first recommendation per message if there are multiple
        recs_deduped = recommendations_df.drop_duplicates(subset=['message_id'], keep='first')
        merged = messages_with_purchase.merge(
            recs_deduped[['message_id', 'recommended_product_id'] +
                         (['confidence'] if 'confidence' in recs_deduped.columns else [])],
            on='message_id',
            how='left'
        )

        # Calculate metrics
        exact_matches = 0
        category_matches = 0
        out_of_stock = 0
        ratings = []
        confidences = []
        recommendations_made = 0

        for _, row in merged.iterrows():
            actual = row['converted_to_purchase']
            recommended = row['recommended_product_id']

            # Skip if no recommendation was made
            if pd.isna(recommended) or recommended is None:
                continue

            recommendations_made += 1

            # Exact match
            if recommended == actual:
                exact_matches += 1

            # Category match
            actual_category = product_categories.get(actual)
            rec_category = product_categories.get(recommended)
            if actual_category and rec_category and actual_category == rec_category:
                category_matches += 1

            # Out of stock
            if product_stock.get(recommended, 0) == 0:
                out_of_stock += 1

            # Rating
            rating = product_ratings.get(recommended)
            if rating:
                ratings.append(rating)

            # Confidence (if available)
            if 'confidence' in row and pd.notna(row['confidence']):
                confidences.append(row['confidence'])

        return AnalysisResult(
            total_messages=len(messages_df),
            messages_with_purchase=len(messages_with_purchase),
            recommendations_made=recommendations_made,
            exact_matches=exact_matches,
            category_matches=category_matches,
            out_of_stock_recommendations=out_of_stock,
            avg_recommended_rating=sum(ratings) / len(ratings) if ratings else 0.0,
            avg_confidence=sum(confidences) / len(confidences) if confidences else None,
        )

    def format_results(self, result: AnalysisResult, name: str = "Recommendations") -> str:
        """Format analysis results as a readable string."""
        lines = [
            f"\n{'='*50}",
            f" {name}",
            f"{'='*50}",
            f"",
            f"Accuracy:",
            f"  Exact Match Rate:      {result.exact_match_rate:>6.1%}  ({result.exact_matches}/{result.messages_with_purchase})",
            f"  Category Match Rate:   {result.category_match_rate:>6.1%}  ({result.category_matches}/{result.messages_with_purchase})",
            f"",
            f"Coverage:",
            f"  Messages with Purchase: {result.messages_with_purchase}/{result.total_messages}",
            f"  Recommendations Made:   {result.recommendations_made}",
            f"  Coverage Rate:          {result.recommendation_coverage:.1%}",
            f"",
            f"Quality:",
            f"  Out-of-Stock Rate:     {result.out_of_stock_rate:>6.1%}",
            f"  Avg Product Rating:    {result.avg_recommended_rating:>6.2f}",
        ]

        if result.avg_confidence is not None:
            lines.append(f"  Avg Confidence:        {result.avg_confidence:>6.2f}")

        lines.append("")
        return "\n".join(lines)
