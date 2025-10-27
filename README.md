# goodparty.org AI Engineer Assessment

**Duration**: 2-3 hours

---

## The Task

Build a product recommendation system for our e-commerce platform. Our current system isn't performing well, and we need you to:

1. **Analyze the historical data** to understand what's broken
2. **Build a better system** informed by historical insights
3. **Validate your approach** with evidence

---

## Datasets

You'll work with three CSV files in the `data/` folder. Explore them to understand the structure and relationships.

---

## Requirements

### What You Need to Build:
1. **Pipeline code** that processes the messages and generates recommendations
2. **Output CSV** with your recommendations for all messages
3. Must use **Gemini API (free tier)** - we'll test with our own API key in free tier

### Output Format
Your output CSV should include:
- `message_id` - links to the original message
- `recommended_product_id` - your recommendation
- `confidence` - score between 0-1
- `reasoning` - why you recommended this product

---

## What to Submit

1. **Pipeline code** 
2. **Output CSV** 
3. **README.md** with explanation on how to run things
4. **Analysis document** (Markdown, PDF, or notebook) covering:
   - Data exploration: What did you discover?
   - Design decisions: Why this approach?
   - Validation: How do you know it's better?

---

## Evaluation

We'll evaluate based on:
- **Implementation**: Does it work well and produce quality recommendations? This includes code organization and quality.
- **Problem-Solving**: Are your decisions justified with evidence?
- **Communication**: Clear documentation and explanations?

---

## Notes

- AI tools are encouraged, but a word of advice, don't use ai to offload your thinking, but instead to extend your thinking. 
- You should be able to explain every detail of this project. Every decision etc.
- Make reasonable assumptions if anything is unclear and document them

Good luck!
AI team at goodparty.orgs