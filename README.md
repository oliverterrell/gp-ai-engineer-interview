# Product Recommendation System

An LLM-powered recommendation pipeline that analyzes user messages and suggests relevant products from an e-commerce catalog.

## Setup
Visit https://aistudio.google.com/api-keys and click "Create API key" on the top-right to create a free-to-use Gemini API key.

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Usage

### Generate Recommendations

```bash
# Process all historical messages → outputs recommendations.csv
python recommend.py

# Custom output path
python recommend.py -o my_recommendations.csv

# Test with a single message (outputs to console)
python recommend.py --message "I need running shoes for a marathon"
```

### Analyze Results

```bash
# Analyze historical recommendation performance
python analyze.py

# Analyze your generated recommendations
python analyze.py -r recommendations.csv

# Compare your recommendations against historical baseline
python analyze.py -r recommendations.csv --compare
```

## How It Works

The recommendation pipeline uses a two-stage LLM approach:

1. **Intent Classification** — Determines if the user has purchase intent and identifies the top 3 relevant product categories
2. **Product Selection** — Filters candidates by category, stock, and rating, then ranks the top 3 products with confidence scores

Output includes `message_id`, `recommended_product_id`, `confidence`, and `reasoning` for a total of three top recommendations.

## Project Structure

```
├── recommend.py      # Main recommendation pipeline
├── analyze.py        # Evaluation script
├── lib/
│   ├── config.py     # API and business rule settings
│   ├── analyzer.py   # Metrics calculation
│   └── utils.py      # Data loading helpers
└── data/
    ├── messages.csv              # User messages
    ├── products.csv              # Product catalog
    └── recommendations_history.csv  # Historical recommendations
```

Supporting files have been left in project root, though don't be alarmed by their presence. Notes in `ANALYSIS.md` can be found explaining what these files contain.