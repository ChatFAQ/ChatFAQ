travel_place_q = """You are tasked with generating an engaging travel-related question based on a list of countries, cities or places. The question should highlight the main themes or experiences associated with each place in the list.

Here is the list of places:
<places_list>
{PLACES_LIST}
</places_list>

To complete this task, follow these steps:

1. For each place in the list, identify one main theme or unique experience that is strongly associated with that place. These themes should be distinct and representative of the country's culture, attractions, or well-known activities.

2. Create a question that incorporates all the themes you've identified, presenting them as options for a hypothetical travel experience. The question should be structured in a way that asks the reader to choose between these experiences.

3. When formulating the question, adhere to these guidelines:
   - Begin with a phrase like "If you could choose o
ne experience for your next trip, would you prefer to..."
   - Present each place's theme as a brief, vivid description
   - Use commas to separate the options, and the word "or" before the final option
   - Aim for a balanced representation of each country's theme
   - Keep the overall question concise and engaging
   - Don't mention the place

4. Ensure that your question flows naturally and is easy to read, while still capturing the essence of each country's unique appeal.

Please provide your generated question within <question> tags."""