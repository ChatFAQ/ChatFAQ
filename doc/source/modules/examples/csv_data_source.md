# Using CSVs as the data source

## Overview

This example demonstrates how ChatFAQ seamlessly handles structured data in a CSV (Comma-Separated Values) format. CSVs are ideal for storing tabular information like product specifications, FAQs, contact lists, and more.  By uploading a CSV, you enable ChatFAQ to directly answer user questions based on its contents.

### Use Cases

- Product Catalogs: Maintain an up-to-date product inventory in a CSV, allowing users to query product details, prices, and availability.
- Frequently Asked Questions (FAQs): Turn common questions and answers into a CSV, transforming ChatFAQ into a self-service knowledge base.
- Dictionaries or Glossaries: Create a CSV of terms and definitions for a specific domain, providing users with quick explanations.

### Benefits of Using CSVs

- Structured format: CSVs organize data clearly, making it easy for ChatFAQ to process.
- Widespread compatibility: CSV files can be created and edited using common spreadsheet software.
- Versatility: CSVs can represent a wide range of simple and complex datasets.

## Prerequisites

- ChatFAQ installation and setup.

### Required CSV Formatting

- **Header Row**: The first row of your CSV must contain the column headers listed below.

Column Header | Data Type | Mandatory? | Description
------------- | --------- | ---------- | -----------
`content`     |   Text    |     Yes    | The core answer or information used to create the answers.
`title`       |   Text    |     No     | A short, descriptive title for the content. This could be the question in the case of FAQs.
`url`         |   Text    |     No     | A link to a more detailed source, external resource, or the original document where the content is derived
  
## Step-by-step guide

1. In the admin go to the Knowledge Base section.
2. Create a new knowledge base.
3. Go to the "Data Source" tab.
4. Add a new data source, select the CSV that you want to use and select the knowledge base that you just created.
5. Click on "Save".

To see the chatbot in action with the new data source, go to the LLM examples guide and follow the instructions to create a new chatbot.
