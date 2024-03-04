# Using PDFs as the data source

## Overview

PDFs are an essential way to store and share a wide range of knowledge. Whether you have technical manuals, product documentation, company policies, research reports, or other structured text, ChatFAQ allows you to easily transform them into a powerful chatbot.

## Prerequisites

- ChatFAQ installation and setup
- A collection of PDFs to use as the data source. If you don't have any, you can use the ChatFAQ sample PDFs.
  
## Step-by-step guide

1. In the admin go to the Knowledge Base section.
2. Create a new knowledge base.
3. Go to the "Data Source" tab.
4. Add a new data source, select the PDFs that you want to use and select the knowledge base that you just created.
5. Select the PDF processing options that you want to use. For information about the options, see the Knowledge Base documentation of the AI Configuration section.
6. Click on "Save".

After these steps you will see that a new task has been created to process the PDFs. This task uses [Unstructured](https://github.com/Unstructured-IO/unstructured) to extract the text from the PDFs and store it in the knowledge base. Once the task is finished, you will see knowledge items extracted from the PDFs.
