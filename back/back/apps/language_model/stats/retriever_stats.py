def calculate_precision(admin_labels, k_items):
    # Count the number of positive labels
    positive_count = sum(1 for label in admin_labels if label['value'] == 'positive')
    
    # Count the total number of labeled items (excluding unlabeled items)
    # I'm not sure if this should be the total number of items or the total number of labeled items
    total_labeled = len([label for label in admin_labels if label['value'] in ['positive', 'negative']])
    
    # Calculate precision
    precision = positive_count / k_items # total_labeled if total_labeled > 0 else 0
    
    return precision


def calculate_recall(admin_labels):
    relevant_labels = ['positive', 'alternative']

    positive_count = sum(1 for label in admin_labels if label['value'] == 'positive')
    
    total_relevant = sum(1 for label in admin_labels if label['value'] in relevant_labels)
    
    recall = positive_count / total_relevant if total_relevant > 0 else 0
    return recall


def calculate_f1(precision, recall):
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0


def calculate_unlabeled_item_rate(retrieved_items, admin_labels):
    labeled_item_ids = {label['knowledge_item_id'] for label in admin_labels}
    total_unlabeled = len(retrieved_items) - len(labeled_item_ids)
    
    unlabeled_item_rate = total_unlabeled / len(retrieved_items) if retrieved_items else 0
    return unlabeled_item_rate


def calculate_retriever_stats(admin_labels, retrieved_items):
    k_items = len(retrieved_items)
    precision = calculate_precision(admin_labels, k_items)
    recall = calculate_recall(admin_labels)
    f1 = calculate_f1(precision, recall)
    unlabeled_item_rate = calculate_unlabeled_item_rate(retrieved_items, admin_labels)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'unlabeled_item_rate': unlabeled_item_rate
    }


