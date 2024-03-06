from django.core.management.base import BaseCommand
from back.apps.language_model.models import KnowledgeBase, KnowledgeItem, KnowledgeItemImage
import requests
import base64
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Migrate knowledge items and images from a source deployment to a destination deployment'
    # command: python manage.py migrate_knowledge_base http://source-deployment.com source_kb_name destination_kb_name --token=token

    def add_arguments(self, parser):
        parser.add_argument('source_back_url', type=str, help='Base URL of the source back deployment')
        parser.add_argument('source_kb_name', type=str, help='Name of the source knowledge base')
        parser.add_argument('destination_kb_name', type=str, help='Name of the destination knowledge base')
        parser.add_argument('--token', type=str, help='Token for header authentication')

    def handle(self, *args, **options):
        source_back_url = options['source_back_url']
        source_kb_name = options['source_kb_name']
        destination_kb_name = options['destination_kb_name']
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
        self.stdout.write(self.style.SUCCESS(f'Found knowledge base "{source_kb_name}" in the source deployment.'))

        # Retrieve knowledge items from the source deployment for the specified knowledge base
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-items/?knowledge_base__name={source_kb_name}', headers=header)
        knowledge_items_data = response.json()

        if knowledge_items_data['count'] == 0:
            self.stdout.write(self.style.ERROR(f'No knowledge items found for knowledge base "{source_kb_name}" in the source deployment.'))
            return
        self.stdout.write(self.style.SUCCESS(f'Found {knowledge_items_data["count"]} knowledge items for knowledge base "{source_kb_name}" in the source deployment.'))

        # Retrieve knowledge item images from the source deployment for the specified knowledge base
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-item-images/?knowledge_item__knowledge_base__name={source_kb_name}', headers=header)
        knowledge_item_images_data = response.json()

        images_data = {} # {knowledge_item_id: [image_data]}
        if knowledge_item_images_data['count'] > 0:
            images_data = {}
            for item_image_data in knowledge_item_images_data['results']:
                knowledge_item_id = item_image_data['knowledge_item']
                if knowledge_item_id not in images_data:
                    images_data[knowledge_item_id] = []
                images_data[knowledge_item_id].append(item_image_data)
            self.stdout.write(self.style.SUCCESS(f'Found {knowledge_item_images_data["count"]} knowledge item images for knowledge base "{source_kb_name}" in the source deployment.'))


        self.stdout.write(f"Saving {len(knowledge_items_data['results'])} knowledge items and {len(images_data.keys())} images...")

        for item_data in tqdm(knowledge_items_data['results']):
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

            # Retrieve and create associated images
            if item_data['id'] in images_data:
                for image_data in images_data[item_data['id']]:
                    image_response = requests.get(image_data['image_file'])
                    image_base64_string = base64.b64encode(image_response.content).decode('utf-8')  # Convert to string

                    image_instance = KnowledgeItemImage(
                        image_base64=image_base64_string,
                        image_caption=image_data['image_caption'],
                        knowledge_item=knowledge_item
                    )
                    image_instance.save()

                    # Modify the knowledge item content to replace the image file path with the new image instance file path
                    knowledge_item.content.replace(image_data['image_file_name'], image_instance.image_file.name)
                    knowledge_item.save()

        self.stdout.write(self.style.SUCCESS('Knowledge items and images migrated successfully.'))