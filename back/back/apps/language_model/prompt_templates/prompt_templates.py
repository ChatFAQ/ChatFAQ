from typing import List

QUERIES_OUT_OF_DOMAIN_EN = """What are the best practices for starting a successful online business?
How can I improve my time management skills and productivity?
What are the most effective ways to deal with stress and anxiety?
How does climate change impact wildlife and ecosystems?
What are the key features to consider when buying a new smartphone?
How can I learn a new language effectively and efficiently?
What are the potential benefits and risks of using AI in healthcare?
How do electric cars contribute to reducing carbon emissions?
What are the current trends in sustainable fashion and ethical clothing brands?
How can I create a balanced and nutritious diet plan for myself?
What are some practical tips for improving public speaking skills?
How does meditation affect the brain and overall mental well-being?
How do online social networks impact human behavior and relationships?
What are some innovative ways that companies are using virtual reality technology?
If you could visit any period in history for a week, when would it be?
What fictional world would you love to be a part of?
Which wild animal would you most want as a pet, assuming it would be friendly and loyal?
If you could master any skill instantly, what would it be?
What's the most unusual food you've ever tried and liked?
Would you rather live without music or without colors?
If our solar system had a tourist agency, which planet or moon would be the top vacation spot?
How do you think smartphones will evolve in the next decade?
If you could switch lives with any historical figure for a day, who would it be?
Which book has had the most impact on your life?
Hello
How are you?
Good morning
Hi
Good afternoon
Thanks
Good evening
Happy Friday
See you later"""


QUERIES_OUT_OF_DOMAIN_FR = """Quelles sont les meilleures pratiques pour créer une entreprise en ligne prospère ?
Comment puis-je améliorer mes compétences en matière de gestion du temps et ma productivité ?
Quels sont les moyens les plus efficaces pour gérer le stress et l'anxiété ?
Quel est l'impact du changement climatique sur la faune et les écosystèmes ?
Quelles sont les principales caractéristiques à prendre en compte lors de l'achat d'un nouveau smartphone ?
Comment puis-je apprendre une nouvelle langue de manière efficace et efficiente ?
Quels sont les avantages et les risques potentiels de l'utilisation de l'IA dans les soins de santé ?
Comment les voitures électriques contribuent-elles à réduire les émissions de carbone ?
Quelles sont les tendances actuelles en matière de mode durable et de marques de vêtements éthiques ?
Comment puis-je me créer un régime alimentaire équilibré et nutritif ?
Quels sont les conseils pratiques pour améliorer ses compétences en matière de prise de parole en public ?
Comment la méditation affecte-t-elle le cerveau et le bien-être mental en général ?
Comment les réseaux sociaux en ligne influencent-ils le comportement humain et les relations ?
Quelles sont les méthodes innovantes utilisées par les entreprises pour utiliser la technologie de la réalité virtuelle ?
Si vous pouviez visiter n'importe quelle période de l'histoire pendant une semaine, quand serait-ce ?
Dans quel monde fictif aimeriez-vous faire partie ?
Quel animal sauvage aimeriez-vous avoir comme animal de compagnie, en supposant qu'il soit amical et loyal ?
Si vous pouviez maîtriser n'importe quelle compétence instantanément, quelle serait-elle ?
Quel est l'aliment le plus inhabituel que vous ayez jamais goûté et aimé ?
Préféreriez-vous vivre sans musique ou sans couleurs ?
Si notre système solaire disposait d'une agence de tourisme, quelle planète ou quelle lune serait le premier lieu de villégiature ?
Comment pensez-vous que les smartphones évolueront au cours de la prochaine décennie ?
Si vous pouviez échanger votre vie avec un personnage historique pour une journée, qui serait-ce ?
Quel livre a eu le plus d'impact sur votre vie ?
Bonjour
Comment allez-vous ?
Bonjour
Bonjour
Bonjour
Merci de votre compréhension
Bonne soirée
Joyeux vendredi
A plus tard"""


QUERIES_OUT_OF_DOMAIN_ES = """¿Cuáles son las mejores prácticas para iniciar con éxito un negocio en línea?
¿Cómo puedo mejorar mi capacidad de gestión del tiempo y mi productividad?
¿Cuáles son los métodos más eficaces para combatir el estrés y la ansiedad?
¿Cómo afecta el cambio climático a la fauna y los ecosistemas?
¿Cuáles son las principales características que hay que tener en cuenta al comprar un nuevo teléfono inteligente?
¿Cómo puedo aprender un nuevo idioma de forma eficaz y eficiente?
¿Cuáles son los beneficios y riesgos potenciales del uso de la IA en la asistencia sanitaria?
¿Cómo contribuyen los coches eléctricos a reducir las emisiones de carbono?
¿Cuáles son las tendencias actuales en moda sostenible y marcas de ropa ética?
¿Cómo puedo elaborar un plan de alimentación equilibrado y nutritivo?
¿Cuáles son algunos consejos prácticos para mejorar la capacidad de hablar en público?
¿Cómo afecta la meditación al cerebro y al bienestar mental en general?
¿Cómo influyen las redes sociales en el comportamiento y las relaciones humanas?
¿Cuáles son algunas de las formas innovadoras en que las empresas utilizan la tecnología de realidad virtual?
Si pudieras visitar cualquier época de la historia durante una semana, ¿cuándo sería?
¿De qué mundo ficticio te gustaría formar parte?
¿Qué animal salvaje le gustaría tener como mascota, suponiendo que fuera amistoso y leal?
Si pudiera dominar cualquier habilidad al instante, ¿cuál sería?
¿Cuál es la comida más inusual que ha probado y le ha gustado?
¿Preferiría vivir sin música o sin colores?
Si nuestro sistema solar tuviera una agencia de turismo, ¿qué planeta o luna sería el principal lugar de vacaciones?
¿Cómo cree que evolucionarán los teléfonos inteligentes en la próxima década?
Si pudiera cambiar de vida con cualquier personaje histórico por un día, ¿quién sería?
¿Qué libro le ha marcado más?
Hola
¿Qué tal?
Buenos días
Hola
Buenas tardes
Gracias
Buenas tardes
Feliz viernes
Hasta luego"""


QUERIES_OUT_OF_DOMAIN = {
    'en': QUERIES_OUT_OF_DOMAIN_EN.split('\n'),
    'fr': QUERIES_OUT_OF_DOMAIN_FR.split('\n'),
    'es': QUERIES_OUT_OF_DOMAIN_ES.split('\n'),
}

def get_queries_out_of_domain(lang: str = 'en') -> List[str]:
    """
    Get queries out of domain.
    Parameters
    ----------
    lang: str
        Language of the queries.
    Returns
    -------
    List[str]
        List of queries.
    """
    return QUERIES_OUT_OF_DOMAIN[lang] if lang in QUERIES_OUT_OF_DOMAIN else QUERIES_OUT_OF_DOMAIN['en']