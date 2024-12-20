import asyncio
from logging import getLogger
import random

import ray
from ray.util.placement_group import (
    placement_group,
    remove_placement_group,
)
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

from back.utils.ray_utils import ray_task

logger = getLogger(__name__)


# Helper functions


def retrieve(queries, kb_id):
    """
    Use BM25 for the initial retrieval and then rerank the results with a cross-encoder.
    We use BM25 for simplicity and speed, because the thing we care the most is getting the scores from the cross-encoder.
    """
    import torch
    from back.apps.language_model.models import KnowledgeBase, KnowledgeItem
    from chat_rag.retrievers import BM25Retriever, ReRankRetriever

    items = KnowledgeItem.objects.filter(knowledge_base=kb_id)
    items = [f"{item.title} {item.content}" for item in items]
    corpus = [{"content": item} for item in items]
    lang = KnowledgeBase.objects.get(pk=kb_id).lang

    top_k = int(0.2 * len(corpus))
    top_k = min(top_k, 10)  # limit the top_k to 20 to avoid long processing times

    retriever = BM25Retriever(corpus)

    # get cuda as device if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size = 32 if device == "cuda" else 1

    rerank_retriever = ReRankRetriever(retriever, lang, device)

    results = rerank_retriever.retrieve(queries, top_k=top_k, batch_size=batch_size)

    return results


def get_placement_group(low_resource):
    if low_resource:
        logger.info("Acquiring a CPU for the low resource clustering task...")
        return placement_group(
            [{"CPU": 1.0, "tasks": 1.0}],
            strategy="STRICT_PACK",
            name="clusterize_texts",
        ), "cpu"
    else:
        logger.info("Acquiring a GPU for the clustering task...")
        return placement_group(
            [{"CPU": 1.0, "GPU": 1.0, "tasks": 1.0}],
            strategy="STRICT_PACK",
            name="clusterize_texts",
        ), "gpu"


def run_clustering_task(knowledge_base_pk, texts, batch_size, lang, low_resource):
    task_name = f"clusterize_texts_{knowledge_base_pk}"
    pg, device = get_placement_group(low_resource)

    try:
        ray.get(pg.ready(), timeout=10)
        scheduling_strategy = PlacementGroupSchedulingStrategy(
            placement_group=pg,
            placement_group_bundle_index=0,
        )
    except Exception:
        if not low_resource:
            logger.info(
                "No GPUs available or placement group creation failed, using CPUs for the task"
            )
        scheduling_strategy = None
        device = "cpu"

    try:
        labels = ray.get(
            clusterize_texts_task.options(
                name=task_name,
                scheduling_strategy=scheduling_strategy,
            ).remote(texts, batch_size, lang, device, low_resource)
        )
        return labels
    except Exception as e:
        raise e
    finally:
        remove_placement_group(pg)


# Tasks

@ray_task(num_cpus=1, resources={"tasks": 1})
def generate_titles_task(knowledge_base_pk, llm_config_id, max_k_items: int = 50):
    """
    Generate titles for the knowledge items of a knowledge base.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    llm_config_id : int
        The LLM to use for generating the titles.
    max_k_items : int, optional
        The maximum number of knowledge items to generate titles, by default 50.
    """

    from back.apps.language_model.models import (
        AutoGeneratedTitle,
        KnowledgeBase,
        KnowledgeItem,
        LLMConfig,
    )
    from chat_rag.llms import load_llm
    from chat_rag.utils.gen_question import agenerate_questions

    kb = KnowledgeBase.objects.get(pk=knowledge_base_pk)
    k_items = KnowledgeItem.objects.filter(knowledge_base=knowledge_base_pk)

    if k_items.count() > max_k_items:
        k_items = random.sample(list(k_items), max_k_items)

    llm_config = LLMConfig.objects.get(pk=llm_config_id)

    llm = load_llm(
        llm_config.llm_type,
        llm_config.llm_name,
        base_url=llm_config.base_url,
        model_max_length=llm_config.model_max_length,
    )

    logger.info(f"Generating questions for {len(k_items)} knowledge items")

    questions = asyncio.run(
        agenerate_questions(
            [f"{item.title} {item.content}" for item in k_items],
            llm,
        )
    )

    auto_gen_questions = []
    for question, item in zip(questions, k_items):
        auto_gen_questions.append(
            AutoGeneratedTitle(
                knowledge_item=item,
                title=question,
            )
        )
    AutoGeneratedTitle.objects.bulk_create(auto_gen_questions)

    logger.info(f"Questions generated for knowledge base: {kb.name}")


@ray_task(num_cpus=1, resources={"tasks": 1})
def generate_intents(clusters_texts, llm_config_id):
    from back.apps.language_model.models import LLMConfig
    from chat_rag.intent_detection import agenerate_intents
    from chat_rag.llms import load_llm

    llm_config = LLMConfig.objects.get(pk=llm_config_id)
    llm = load_llm(
        llm_config.llm_type,
        llm_config.llm_name,
        base_url=llm_config.base_url,
        model_max_length=llm_config.model_max_length,
    )

    logger.info("Generating intents...")
    intents = asyncio.run(agenerate_intents(clusters_texts, llm))
    return intents


@ray_task(num_cpus=1, resources={"tasks": 1}, num_returns=2)
def get_similarity_scores(titles, kb_id):
    import numpy as np

    results = retrieve(titles, kb_id)

    similarities = [item[0]["score"] for item in results]
    mean_similarity = np.mean(similarities)
    std_similarity = np.std(similarities)

    return mean_similarity, std_similarity


@ray_task(num_cpus=1.0, resources={"tasks": 1.0})
def clusterize_texts_task(texts, batch_size, lang, device, low_resource):
    from chat_rag.intent_detection import clusterize_text

    labels = clusterize_text(
        texts=texts,
        batch_size=batch_size,
        lang=lang,
        device=device,
        low_resource=low_resource,
    )
    return labels


@ray_task(num_cpus=0.5, resources={"tasks": 1})
def generate_intents_task(
    knowledge_base_pk, batch_size: int = 32, low_resource: bool = True
):
    """
    Generate existing intents from a knowledge base. Orchestrator task that calls the other tasks.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    batch_size : int, optional
        Batch size for the embedding model, by default 32.
    low_resource : bool, optional
        If True, uses TF-IDF for vectorization, by default False.
    """

    from back.apps.language_model.models import (
        Intent,
        KnowledgeBase,
        KnowledgeItem,
        RetrieverConfig,
    )

    retriever_conf = RetrieverConfig.objects.filter(knowledge_base=knowledge_base_pk).first()
    if not retriever_conf:
        logger.error(
            f"No retriever config found for knowledge base: {knowledge_base_pk}, please create one first so the intents can be generated."
        )
        return

    kb = KnowledgeBase.objects.get(pk=knowledge_base_pk)
    lang = kb.get_lang().value

    k_items = KnowledgeItem.objects.filter(knowledge_base=knowledge_base_pk)

    # the texts are a concatenation of the title and the content
    texts = [
        f"{item.title} {item.content}" for item in k_items
    ]  # concatenate the title and the content

    logger.info(f"Generating intents for {k_items.count()} knowledge items")

    logger.info("Clusterizing texts...")
    labels = run_clustering_task(
        knowledge_base_pk, texts, batch_size, lang, low_resource
    )

    k_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    logger.info(f"Number of clusters: {k_clusters}")

    # dict of lists of texts associated to each cluster
    clusters = {}
    cluster_k_item_instances = {}
    for label, text, k_item in zip(labels, texts, k_items):
        if label != -1:  # -1 is the label for outliers
            if label not in clusters:
                clusters[label] = []
                cluster_k_item_instances[label] = []
            clusters[label].append(text)
            cluster_k_item_instances[label].append(k_item)

    # generate the intents
    logger.info("Generating intents...")
    task_name = f"generate_intents_{knowledge_base_pk}"
    intents = ray.get(
        generate_intents.options(name=task_name).remote(
            clusters, retriever_conf.llm_config.pk
        )
    )

    logger.info(f"Number of new intents: {len(intents)} generated")

    # save the intents
    new_intents = [
        Intent(
            intent_name=intent,
            auto_generated=True,
            valid=False,
            suggested_intent=False,
        )
        for intent in intents
    ]

    Intent.objects.bulk_create(new_intents)

    logger.info("Suggested intents saved successfully")

    # add the knowledge items to each intent
    for (_, items), intent in zip(cluster_k_item_instances.items(), new_intents):
        intent.knowledge_item.add(*items)

    logger.info("Knowledge items added to the intents successfully")


@ray_task(num_cpus=0.5, resources={"tasks": 1})
def generate_suggested_intents_task(
    knowledge_base_pk, batch_size: int = 32, _generate_titles=False, low_resource=True
):
    """
    Generate suggested intents from the users' queries. Here we try to segment the queries that are in domain but do not have a response in the knowledge base yet.
    This implementation is still in progress and can be improved a lot, the results currently are not very good.
    Orchestrator task that calls the other tasks.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    batch_size : int, optional
        Batch size for the embedding model, by default 32.
    _generate_titles : bool, optional
        If True, generates titles for the knowledge items, by default False.
    low_resource : bool, optional
        If True, uses TF-IDF for vectorization, by default False.
    """

    from django.db.models import OuterRef, Subquery
    from back.apps.broker.models.message import AgentType
    from back.apps.broker.models.message import Message
    from back.apps.language_model.models import (
        AutoGeneratedTitle,
        Intent,
        RetrieverConfig,
    )
    from back.apps.language_model.prompt_templates import get_queries_out_of_domain

    retriever_config = RetrieverConfig.objects.filter(knowledge_base=knowledge_base_pk).first()
    if not retriever_config:
        logger.error(
            f"No retriever config found for knowledge base: {knowledge_base_pk}, please create one first so the intents can be generated."
        )
        return

    if _generate_titles:
        task_name = f"generate_titles_{knowledge_base_pk}"
        # block until the task is finished
        ray.get(
            generate_titles_task.options(name=task_name).remote(
                knowledge_base_pk, retriever_config.llm_config.pk
            )
        )

    # These are in domain titles
    titles_in_domain = AutoGeneratedTitle.objects.filter(
        knowledge_item__knowledge_base=knowledge_base_pk
    )[:100]

    lang = retriever_config.knowledge_base.get_lang().value

    task_name = f"get_similarity_scores_{knowledge_base_pk}_in_domain"
    titles_in_domain_str = [title.title for title in titles_in_domain]
    in_domain_task_ref = get_similarity_scores.options(name=task_name).remote(
        titles_in_domain_str,
        knowledge_base_pk,
    )

    task_name = f"get_similarity_scores_{knowledge_base_pk}_out_domain"
    title_out_domain = get_queries_out_of_domain(lang)
    out_domain_task_ref = get_similarity_scores.options(name=task_name).remote(
        title_out_domain,
        knowledge_base_pk,
    )

    mean_sim_in_domain, std_sim_in_domain = ray.get(in_domain_task_ref)
    mean_sim_out_domain, std_sim_out_domain = ray.get(out_domain_task_ref)

    logger.info(
        f"Mean similarity in domain: {mean_sim_in_domain}, std: {std_sim_in_domain}"
    )
    logger.info(
        f"Mean similarity out domain: {mean_sim_out_domain}, std: {std_sim_out_domain}"
    )

    # The suggested new intents will have a similarity score between the in domain queries and the out of domain queries
    new_intents_thresholds = {
        "max": mean_sim_in_domain - (std_sim_in_domain * 2),
        "min": mean_sim_out_domain + std_sim_out_domain,
    }

    logger.info(f"Suggested intents thresholds: {new_intents_thresholds}")

    # check that the max is greater than the min
    if new_intents_thresholds["max"] < new_intents_thresholds["min"]:
        logger.info(
            "Max threshold is lower than min threshold, no new intents will be generated"
        )
        return

    subquery = (
        Message.objects.filter(
            stack__contains=[
                {
                    "payload": {"references": {"knowledge_base_id": knowledge_base_pk}},
                    # "type": "rag_generated_text",
                }
            ]
        )
        .annotate(
            stack_element=Subquery(
                Message.objects.filter(id=OuterRef("id")).values("stack")[:1]
            )
        )
        .values("prev_id")
    )

    # Main query to get the messages where id is in the subquery result
    messages = Message.objects.filter(id__in=Subquery(subquery), sender__type=AgentType.human.value)

    messages_text = [
        Message.objects.get(id=item["message_id"]).stack[0]["payload"]["content"]
        for item in messages
    ]

    logger.info(f"Number of messages: {messages.count()}")

    # Get the scores for the messages.
    results = retrieve(messages_text, knowledge_base_pk)

    # Keep the messages that have a score between the thresholds
    messages = [
        message
        for message, result in zip(messages, results)
        if new_intents_thresholds["min"]
        < result[0]["score"]
        < new_intents_thresholds["max"]
    ]

    messages_text = [message.stack[0]["payload"]["content"] for message in messages]

    logger.info(f"Number of messages after filtering: {messages.count()}")

    if messages.count() == 0:
        logger.info("There are no suggested intents to generate")
        return

    logger.info("Clusterizing texts...")
    labels = run_clustering_task(
        knowledge_base_pk, messages_text, batch_size, lang, low_resource
    )

    k_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    logger.info(f"Number of clusters: {k_clusters}")

    # list of lists of queries associated to each cluster
    clusters = [[] for _ in range(k_clusters)]
    cluster_instances = [[] for _ in range(k_clusters)]
    for label, query, message_instace in zip(labels, messages_text, messages):
        if label != -1:  # -1 is the label for outliers
            clusters[label].append(query)
            cluster_instances[label].append(message_instace)

    task_name = f"generate_intents_{knowledge_base_pk}"
    intents = ray.get(
        generate_intents.options(name=task_name).remote(
            clusters, retriever_config.llm_config.pk
        )
    )

    new_intents = [
        Intent(
            intent_name=intent,
            auto_generated=True,
            valid=False,
            suggested_intent=True,
        )
        for intent in intents
    ]

    Intent.objects.bulk_create(new_intents)

    logger.info(f"Number of new intents: {len(new_intents)}")

    # add the messages to each intent
    for intent_cluster, intent in zip(cluster_instances, new_intents):
        # get the value of key 'message_id' from each message
        intent_cluster = [item["message_id"] for item in intent_cluster]
        intent.message.add(*intent_cluster)

    logger.info("New intents generated successfully")
