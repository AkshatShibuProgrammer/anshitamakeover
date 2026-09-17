from django.utils.text import slugify
from core.models import Artist

def list_all_artists():
    """Retrieve all artists as serializable list of dictionaries"""
    artists = []
    for a in Artist.objects.all():
        artists.append({
            'id': a.id,
            'name': a.name,
            'slug': a.slug,
            'bio': a.bio,
            'specialities': a.specialities,
            'photo_url': a.photo.url if a.photo else '',
            'order': a.order,
            'is_active': a.is_active
        })
    return {'artists': artists}

def delete_artist_by_id(artist_id):
    """Delete artist record by primary key"""
    if not artist_id:
        return {'ok': False, 'error': 'Artist ID is required.'}
    Artist.objects.filter(id=artist_id).delete()
    return {'ok': True}

def save_artist_record(data, files):
    """Create or update an artist model record"""
    artist_id = data.get('id')
    name = data.get('name', '').strip()
    if not name:
        return {'ok': False, 'error': 'Artist name is required.'}

    specialities = data.get('specialities', 'makeup').strip()
    bio = data.get('bio', '').strip()
    order_val = data.get('order', 0)
    try:
        order = int(order_val)
    except (ValueError, TypeError):
        order = 0
    is_active = data.get('is_active') != '0'

    if artist_id:
        try:
            artist = Artist.objects.get(id=artist_id)
            artist.name = name
            artist.specialities = specialities
            artist.bio = bio
            artist.order = order
            artist.is_active = is_active
        except Artist.DoesNotExist:
            return {'ok': False, 'error': 'Artist not found.'}
    else:
        base_slug = slugify(name) or 'artist'
        slug = base_slug
        idx = 1
        while Artist.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{idx}"
            idx += 1
        artist = Artist(
            name=name,
            slug=slug,
            specialities=specialities,
            bio=bio,
            order=order,
            is_active=is_active
        )

    if files and 'photo' in files:
        artist.photo = files['photo']

    artist.save()
    return {
        'ok': True,
        'artist': {
            'id': artist.id,
            'name': artist.name,
            'specialities': artist.specialities,
            'bio': artist.bio,
            'photo_url': artist.photo.url if artist.photo else '',
            'order': artist.order,
            'is_active': artist.is_active
        }
    }
