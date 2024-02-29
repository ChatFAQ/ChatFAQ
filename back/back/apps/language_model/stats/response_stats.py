from typing import List
from back.apps.broker.models.message import AdminReview, UserFeedback


def calculate_response_stats(admin_reviews: List[AdminReview], user_feedbacks: List[UserFeedback]):
    # get the quality values
    admin_quality_values = [admin_review.gen_review_val for admin_review in admin_reviews]
    user_quality_values = [user_feedback.value for user_feedback in user_feedbacks]
    
    # Compute the average value and normalize to 0-1
    admin_quality = sum(admin_quality_values) / len(admin_quality_values) if admin_quality_values else 0
    scale = max(AdminReview.VALUE_CHOICES)[0]
    admin_quality = admin_quality / scale  # normalize
    

    # map user feedback from positive/negative to 1/0 and compute the average
    user_quality_values = [1 if user_feedback == "positive" else 0 for user_feedback in user_quality_values]
    user_quality = sum(user_quality_values) / len(user_quality_values) if user_quality_values else 0

    return {
        'admin_quality': admin_quality,
        'user_quality': user_quality
    }