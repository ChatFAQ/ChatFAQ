from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from back.apps.language_model.models import KnowledgeBase, KnowledgeItem, KnowledgeItemImage
import requests


class Command(BaseCommand):
    help = 'Migrate knowledge items and images from a source deployment to a destination deployment'
    # command: python manage.py migrate_knowledge_items http://source-deployment.com source_kb_name destination_kb_name --token=token

    def add_arguments(self, parser):
        parser.add_argument('source_base_url', type=str, help='Base URL of the source deployment')
        parser.add_argument('source_base_name', type=str, help='Name of the source knowledge base')
        parser.add_argument('destination_base_name', type=str, help='Name of the destination knowledge base')
        parser.add_argument('--token', type=str, help='Token for header authentication')

    def handle(self, *args, **options):
        source_back_url = options['source_base_url']
        source_kb_name = options['source_base_name']
        destination_kb_name = options['destination_base_name']
        token = options['token']
        header = {'Authorization': f'Token {token}'} if token else {}

        # Retrieve the destination knowledge base by name
        try:
            destination_base = KnowledgeBase.objects.get(name=destination_kb_name)
        except KnowledgeBase.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No knowledge base found with name "{destination_kb_name}" in the destination deployment.'))
            return

        # Retrieve the source knowledge base by name to check if it exists
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-bases/?name={source_kb_name}', headers=header)
        source_base_data = response.json()

        if not source_base_data:
            self.stdout.write(self.style.ERROR(f'No knowledge base found with name "{source_kb_name}" in the source deployment.'))
            return

        # Retrieve knowledge items from the source deployment for the specified knowledge base
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-items/?knowledge_base__name={source_kb_name}', headers=header)
        knowledge_items_data = response.json()

        if knowledge_items_data['count'] == 0:
            self.stdout.write(self.style.ERROR(f'No knowledge items found for knowledge base "{source_kb_name}" in the source deployment.'))
            return

        for item_data in knowledge_items_data:
            # Create a new knowledge item in the destination deployment
            knowledge_item = KnowledgeItem(
                knowledge_base=destination_base,
                title=item_data['title'],
                content=item_data['content'],
                url=item_data['url'],
                section=item_data['section'],
                role=item_data['role'],
                page_number=item_data['page_number'],
                metadata=item_data['metadata']
            )
            knowledge_item.save()

            # # Retrieve and create associated images
            # images_data = item_data['images']
            # for image_data in images_data:
            #     image_response = requests.get(image_data['image_url'])
            #     image_content = ContentFile(image_response.content)
            #     knowledge_item_image = KnowledgeItemImage(
            #         knowledge_item=knowledge_item,
            #         image_caption=image_data['image_caption']
            #     )
            #     knowledge_item_image.image_file.save(image_data['image_name'], image_content)
            #     knowledge_item_image.save()

        self.stdout.write(self.style.SUCCESS('Knowledge items and images migrated successfully.'))