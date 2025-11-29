# Analysis Document – Dev Notes


## Legacy System Issues

---
Analyzing the data, I uncovered the following glaring issues with the legacy system:

1. 0% success rate indicates critical issue with feature.

2. Recommend one product a large number of times, indicates the recommendation engine perhaps errored somewhere and is defaulting to a fallback product. This could lead to negative user experience,
   so fallbacks should be handled differently in the new system.

3. The system appears to ignore product categories. If we have that information, we can likely leverage it for better outcomes.

4. Appears to recommend based on keyword only, ignoring sentiment. Engine should care if the user is saying positive or negative things.

5. Continuously recommends out-of-stock products. Out-of-stock products should only be recommended if there is a "pre-order" or similar feature. Without direct lead to a sale, a recommendation should not occur.

6. System appears to ignore product rating. Ratings are highly important and should be factored into whether or not a product is recommended.

7. Recommendations are succeeding in getting a click, but failing entirely to generate purchases. This indicates users want to be led and this is a good focus area.


## Recommend.py

---
The `recommend.py` script serves two functions. It can process a `recommendations_history.csv` (default) to generate an output CSV containing recommendations in the format requested, and it also
will provide a one-off recommendation output for a novel user message passed via command line. View the comment at the top of the script file for instructions on how to run.

Recommend will make two API calls to the Gemini LLM, using free model `gemini-2.5-flash-lite`. Gemini 2.5 Flash Lite has best-in-class rate limits and daily usage limits for any generative model in Google's free tier, though the rate limits are quite restrictive for a production system.
Read the **Embeddings & Financial Optimization** section below for more notes related to this observation.

##  Analysis.py

---
Since analyzing for issues is listed as a top item in the project scope, and we need to validate performance of the new system, I felt it best to create an analysis script that can analyze the performance of any
recommendation output data. I made analyze.py to capture some performance KPI's and included a comparison flag to show direct comparison between two sets of data from two different systems.

This analysis script could take many forms. We are really just sending a bulk set of messages, recommendations, and user behavior to an LLM and asking it for whatever metrics we want. I used some default metrics here, but imagine whatever we want to cover that can be done via math/statistics or via LLM analysis.

Console output from comparing new results to the old results can be seen in `comparison.txt`.


## Embeddings, Financial Optimization, and Future Scope

---
This project exclusively uses the free tier of Google's AI Studio. The API key generated from the link provided doesn't require a billing account and will never draw a cost. That said, the rate limits are pretty brutal...

My initial instinct was to deliver a system that can handle thousands of concurrent users sending messages and expecting real-time recommendations to come back. I started by trying to leverage **vector embeddings** using a free, locally instantiated model through Python package Sentence Transformers. This was handled inside a script called `embed.py` that was actually removed from the final deliverable.
This script took the product directory and the message history, along with some static premade words and phrases to indicate things like user sentiment or purchase intent, and created local vector embeddings in a `.cache` dir.
When a new message would come in, these stored vector embeddings would be used to match:
1. Prior messages to products that were purchased
2. Purchase intent to determine whether or not to recommend
3. Product descriptions and categories cosine similarity matching to pre-filter requests to the LLM

The embeddings approach was abandoned and described here for a few reasons:
1. Looking at the message history, it is clear that this system only needs to support recommendations at 1 per 15 minutes, as this is the rate of incoming messages. The system is likely operating via email or some not-real-time chat interface where the free tier rate limits are more than encompassing to handle the need.
2. Given how much more room we have against the rate limit, we can afford to make more than one call to the LLM per recommendation request. This allows us to make an initial call to prefilter the product catalogue or intent to buy before generating a recommendation, preserving support for a product catalogue at a scale beyond the token limit of the LLM.
3. Output from a recommendation run using only embeddings can be seen in `scratch.txt`. The accuracy was too low to be shipped to a production system, and given the time constraints it made more sense to leverage the extra room we have on Gemini's free tier to handle the embeddings use case.

To continue to save costs, we could expand the embeddings to perform this functionality. In the time allotted for this project, a suitable embeddings architecture was not feasible and the two LLM calls per recommendation performed with a much higher accuracy than even a well-engineered embeddings architecture would have.
