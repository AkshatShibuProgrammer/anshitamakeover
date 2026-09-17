from core.models import CustomerReview

def create_customer_review(data):
    """Create a verified public customer review"""
    name = data.get('client_name', '').strip()
    review_text = data.get('review_text', '').strip()
    event_type = data.get('event_type', 'Bridal Makeover').strip()
    location = data.get('location', '').strip()
    rating = int(data.get('rating', 5))
    wedding_date = data.get('wedding_date', '').strip()

    if not name or not review_text:
        return {'ok': False, 'error': 'Name and review text are required.'}

    rating = max(1, min(5, rating))
    review = CustomerReview.objects.create(
        client_name=name,
        event_type=event_type or 'Royal Bride',
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
