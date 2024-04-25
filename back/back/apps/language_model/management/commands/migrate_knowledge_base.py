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
        parser.add_argument('--token', type=str, help='Token for header authentication of the source deployment', default='')
        parser.add_argument('--batch-size', type=int, help='Batch size for pagination', default=100)
        parser.add_argument('--offset', type=int, help='Offset for pagination', default=0)

    def retrieve_kb_name(self, source_back_url, source_kb_name, header):
        '''
        Retrieve the source knowledge base by name to check if it exists
        '''
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-bases/?name={source_kb_name}', headers=header)
        source_base_data = response.json()

        if not source_base_data:
            self.stdout.write(self.style.ERROR(f'No knowledge base found with name "{source_kb_name}" in the source deployment.'))
            return False
        
        self.stdout.write(self.style.SUCCESS(f'Found knowledge base "{source_kb_name}" in the source deployment.'))
        return True
    
    def retrieve_knowledge_item_images(self, source_back_url, knowledge_item_ids, header):
        '''
        Retrieve knowledge item images from the source deployment for the specified knowledge items.
        '''

        ids_string = ",".join(map(str, knowledge_item_ids))

        # Retrieve the knowledge item images count for the specified knowledge base
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-item-images/?knowledge_item__id__in={ids_string}&limit=1', headers=header)
        knowledge_item_images_count = response.json()['count']

        # Retrieve knowledge item images from the source deployment for the specified knowledge base
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-item-images/?knowledge_item__id__in={ids_string}&limit={knowledge_item_images_count}', headers=header)
        knowledge_item_images_data = response.json()

        images_data = {} # {knowledge_item_id: [image_data]}
        if knowledge_item_images_data['count'] > 0:
            images_data = {}
            for item_image_data in knowledge_item_images_data['results']:
                knowledge_item_id = item_image_data['knowledge_item']
                if knowledge_item_id not in images_data:
                    images_data[knowledge_item_id] = []
                images_data[knowledge_item_id].append(item_image_data)

        return images_data
    
    def saving_items(self, knowledge_items, images_data, destination_base):
        '''
        Save knowledge items and images to the destination deployment
        '''

        for item_data in knowledge_items:
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
                    content = knowledge_item.content.replace(image_data['image_file_name'], image_instance.image_file.name)
                    knowledge_item.content = content
                    knowledge_item.save()

    
    def migrate_knowledge_items(self, source_back_url, source_kb_name, destination_base, starting_offset, batch_size, header):
        '''
        Retrieve the knowledge items count for the specified knowledge base.
        '''
        response = requests.get(f'{source_back_url}/api/language-model/knowledge-items/?knowledge_base__name={source_kb_name}&limit=1', headers=header)
        knowledge_items_count = response.json()['count']

        self.stdout.write(self.style.SUCCESS(f'Found {knowledge_items_count} knowledge items in the source deployment for knowledge base "{source_kb_name}".'))
        self.stdout.write(self.style.SUCCESS('Saving knowledge items and images...'))

        # We do pagination to not overload the source deployment or the destination deployment
        for offset in tqdm(range(starting_offset, knowledge_items_count, batch_size), desc="Retrieving knowledge items", unit="batch"):
            response = requests.get(f'{source_back_url}/api/language-model/knowledge-items/?knowledge_base__name={source_kb_name}&limit={batch_size}&offset={offset}', headers=header)
            knowledge_items_data = response.json()

            images_data = {}
            if knowledge_items_data['count'] > 0:
                knowledge_item_ids = [item['id'] for item in knowledge_items_data['results']]
                images_data = self.retrieve_knowledge_item_images(source_back_url, knowledge_item_ids, header)

            self.saving_items(knowledge_items_data['results'], images_data, destination_base)

    def handle(self, *args, **options):
        source_back_url = options['source_back_url']
        source_kb_name = options['source_kb_name']
        destination_kb_name = options['destination_kb_name']
        token = options['token']
        batch_size = options['batch_size']
        starting_offset = options['offset']
        header = {'Authorization': f'Token {token}'} if token else {}

        # Retrieve the destination knowledge base by name
        try:
            destination_base = KnowledgeBase.objects.get(name=destination_kb_name)
        except KnowledgeBase.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No knowledge base found with name "{destination_kb_name}" in the destination deployment.'))
            return
        
        # Check if the source knowledge base exists
        if not self.retrieve_kb_name(source_back_url, source_kb_name, header):
            return
        
        # Retrieve knowledge items from the source deployment for the specified knowledge base
        self.migrate_knowledge_items(source_back_url, source_kb_name, destination_base, starting_offset, batch_size, header)