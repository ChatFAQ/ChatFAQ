# Migrate Knowledge Items and Images Command

## Overview

This Django command migrates knowledge items and images from a knowlegde base from a source deployment to a knowledge base in a destination deployment. It is useful for synchronizing or moving content between different instances of a Django application.

## Requirements

- Django framework
- Requests library for HTTP requests
- Access to the Django models: `KnowledgeBase`, `KnowledgeItem`, `KnowledgeItemImage`

## Usage

The command is to be executed from the **destination** back component with the following syntax:

```bash
python manage.py migrate_knowledge_base <source_base_url> <source_kb_name> <destination_kb_name> --token=<token>
```

### Parameters

- `source_base_url`: The base URL of the source deployment.
- `source_kb_name`: The name of the knowledge base in the source deployment.
- `destination_kb_name`: The name of the knowledge base in the destination deployment.
- `--token`: The token to authenticate the request to the source deployment. To generate the token use the following command:

```bash
curl -X POST -u username:password http://develop.your-deploy.com/back/api/login/
```

## Command Details

The command performs the following steps:

1. Validates the existence of the specified knowledge bases in both source and destination deployments.
2. Fetches knowledge items and their associated images from the source deployment.
3. Creates new knowledge items in the destination deployment with the fetched content.
4. Downloads and re-uploads images associated with each knowledge item to the destination deployment.
5. Updates the content of migrated knowledge items to reference the new image paths.

The command might take some time for large knowledge bases with many images.

## Error Handling

- If the source or destination knowledge base does not exist, the command will terminate and report an error.
- The command also reports errors for HTTP requests failures or if no knowledge items are found in the source knowledge base.

## Example

Let's consider a scenario where we want to migrate knowledge items from a source deployment with the URL `http://develop.your-deploy.com/back` and the knowledge base name `chatfaq` to a destination deployment with the knowledge base name `chatfaq`. The source deployment requires a token `123456789` for API access.

```bash
python manage.py migrate_knowledge_base http://develop.your-deploy.com/back chatfaq chatfaq --token=123456789
```

## Notes

- Ensure the source deployment is accessible and the provided URL is correct.
- The --token parameter may be necessary if the source deployment requires authentication for API access.
