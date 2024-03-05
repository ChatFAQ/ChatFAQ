# Using PDFs as the data source

## Overview

PDFs are an essential way to store and share a wide range of knowledge. Whether you have technical manuals, product documentation, company policies, research reports, or other structured text, ChatFAQ allows you to easily transform them into a powerful chatbot.

## Prerequisites

- ChatFAQ installation and setup.
- A collection of PDFs to use as the data source. If you don't have any, you can download this sample PDF: [sample.pdf](https://dergipark.org.tr/en/download/article-file/3307311).
  
## Step-by-step guide

1. In the admin go to the Knowledge Base section.
2. Create a new knowledge base.
3. Go to the "Data Source" tab.
4. Add a new data source, select the PDFs that you want to use and select the knowledge base that you just created.
5. Select the PDF processing options that you want to use. For information about the multiple options like strategy or chunk size, see the [Knowledge Base documentation](../configuration/index.md#pdf-and-url-parsing-options) in the AI Configuration section. For the sample PDF let's choose 384 as chunk size, 16 as chunk overlap, `fast` strategy and `sentences` splitter.
6. Click on "Save".

After these steps you will see that a new task has been created to process the PDFs. This task uses [Unstructured](https://github.com/Unstructured-IO/unstructured) to extract the text from the PDFs and store it in the knowledge base. Once the task is finished, you will see knowledge items extracted from the PDFs in the knowledge items tab.
