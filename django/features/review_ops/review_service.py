from core.models import CustomerReview
from core.security import sanitize_text

# Field budgets (audit §7.1): reviews are publicly rendered, so every free-text
# field is sanitised at the service layer — the single place that writes rows.
MAX_REVIEW_NAME_CHARS = 80
MAX_REVIEW_TEXT_CHARS = 1200
MAX_REVIEW_EVENT_CHARS = 60
MAX_REVIEW_LOCATION_CHARS = 60
MAX_REVIEW_DATE_CHARS = 40


def _safe_rating(value):
    """Coerce any client-supplied value into an int in 1..5 without raising."""
    try:
        rating = int(str(value).strip() or 5)
    except (TypeError, ValueError):
        rating = 5
    return max(1, min(5, rating))


def create_customer_review(data):
    """Create a verified public customer review.

    All string fields pass through ``sanitize_text`` (HTML-stripping +
    control-character removal) and are length-capped, so a review can never
    smuggle markup, script tags, or an oversized payload into the public
    testimonials section.
    """
    data = data if isinstance(data, dict) else {}
    name = sanitize_text(str(data.get('client_name', '')), max_length=MAX_REVIEW_NAME_CHARS)
    review_text = sanitize_text(str(data.get('review_text', '')), max_length=MAX_REVIEW_TEXT_CHARS)
    event_type = sanitize_text(str(data.get('event_type', '')) or 'Bridal Makeover',
                               max_length=MAX_REVIEW_EVENT_CHARS)
    location = sanitize_text(str(data.get('location', '')), max_length=MAX_REVIEW_LOCATION_CHARS)
    rating = _safe_rating(data.get('rating', 5))
    wedding_date = sanitize_text(str(data.get('wedding_date', '')), max_length=MAX_REVIEW_DATE_CHARS)

    if not name or not review_text:
        return {'ok': False, 'error': 'Name and review text are required.'}

    review = CustomerReview.objects.create(
        client_name=name,
        event_type=event_type or 'Bridal Makeover',
        location=location or 'India',
        rating=rating,
        review_text=review_text,
        wedding_date=wedding_date,
        is_verified=True,
        is_active=True,
        order=0
    )
    return {
        'ok': True,
        'message': 'Thank you! Your verified review has been submitted.',
        'review_id': review.id
    }

def handle_admin_review_action(data):
    """Admin moderation for customer reviews"""
    action = data.get('action')
    rev_id = data.get('id')

    if action == 'delete' and rev_id:
        CustomerReview.objects.filter(id=rev_id).delete()
        return {'ok': True}

    if action == 'toggle_active' and rev_id:
        r = CustomerReview.objects.filter(id=rev_id).first()
        if r:
            r.is_active = not r.is_active
            r.save()
            return {'ok': True, 'is_active': r.is_active}

    reviews = list(CustomerReview.objects.all().values())
    return {'reviews': reviews}
