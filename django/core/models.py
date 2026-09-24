from django.db import models
from django.contrib.auth.models import User


class SiteSettings(models.Model):
    """Global site settings controllable by admin"""
    whatsapp_number = models.CharField(max_length=20, default='917879223442')
    instagram_url = models.URLField(default='https://www.instagram.com/anshitamakeover21/')
    youtube_url = models.URLField(default='https://www.youtube.com/@anshitamakeover21', blank=True)
    facebook_url = models.URLField(default='https://www.facebook.com/anshitamakeover21', blank=True)
    
    # Coupon settings
    coupon_active = models.BooleanField(default=True)
    coupon_code = models.CharField(max_length=50, default='GLAMOUR30')
    coupon_discount_percent = models.IntegerField(default=30)
    coupon_label = models.CharField(max_length=200, default='Seasonal Privilege Offer on Bridal Suites & Packages')
    coupon_auto_by_date = models.BooleanField(default=True, help_text='Auto change coupon based on date of month')

    # Exit-Intent / Go-Back Secret Coupon
    exit_coupon_active = models.BooleanField(default=True)
    exit_coupon_code = models.CharField(max_length=50, default='SECRET10')
    exit_coupon_discount_percent = models.IntegerField(default=10)
    exit_coupon_label = models.CharField(max_length=200, default='Exclusive Secret Privilege: Extra 10% Additional Discount')

    # Booking Offer Mechanics & Bundle Privilege Rules (Admin & AI Configurable)
    offer_bridal_free_sides = models.IntegerField(default=2, help_text='Number of free side makeups with bridal booking')
    offer_next_sides_discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=2500.00, help_text='Special discounted price for 3rd and 4th side makeups')
    offer_combo_discount_percent = models.IntegerField(default=15, help_text='Extra discount % when booking Bridal + Engagement')
    offer_grand_combo_bundle_price = models.DecimalField(max_digits=10, decimal_places=2, default=50000.00, help_text='Flat package price for Grand Royal Bridal + Engagement bundle')
    offer_rules_active = models.BooleanField(default=True, help_text='Enable custom booking offer privilege rules')

    # Travel & Outstation Pricing Configuration
    travel_widget_active = models.BooleanField(default=True, help_text='Show outstation travel estimator widget on homepage')
    travel_same_zone_km = models.IntegerField(default=100, help_text='Radius (km) considered same zone with no extra travel charge')
    travel_near_label = models.CharField(max_length=200, default='Nearby Cities (100–400 km)', help_text='Label for near outstation zone')
    travel_near_fee_min = models.IntegerField(default=8000, help_text='Near outstation minimum travel fee (₹)')
    travel_near_fee_max = models.IntegerField(default=15000, help_text='Near outstation maximum travel fee (₹)')
    travel_far_label = models.CharField(max_length=200, default='Pan-India Destination (400+ km)', help_text='Label for far outstation zone')
    travel_far_fee_min = models.IntegerField(default=20000, help_text='Far outstation minimum travel fee (₹)')
    travel_far_fee_max = models.IntegerField(default=40000, help_text='Far outstation maximum travel fee (₹)')
    travel_custom_note = models.CharField(max_length=500, default='Round-trip travel (train/air) + hotel accommodation + local transport for artist & 1 assistant provided by client. Minimum package value ₹50,000+ for outstation bookings.', help_text='Custom note displayed in travel widget')
    # Default Auto-Applied Today's Special & VIP Coupon System
    default_auto_coupon_active = models.BooleanField(default=True, help_text="Automatically apply today's special discount code")
    default_auto_coupon_code = models.CharField(max_length=50, default='TODAYVIP', help_text="Default auto-applied coupon code")
    default_auto_coupon_discount = models.IntegerField(default=15, help_text="Discount percent or flat discount")
    default_auto_coupon_type = models.CharField(max_length=20, default='percent', choices=[('percent', '% Percentage'), ('flat', '₹ Flat Amount')])
    default_auto_coupon_badge = models.CharField(max_length=250, default="⚡ TODAY'S EXCLUSIVE DEAL: Extra 15% VIP Privilege applied automatically today!")
    vip_generated_codes = models.TextField(blank=True, default='[]', help_text="JSON list of generated VIP access codes")

    # AI Price Negotiation Range & Floor Controls
    ai_negotiation_enabled = models.BooleanField(default=True, help_text="Enable AI smart price negotiation")
    ai_negotiation_min_floor_percent = models.IntegerField(default=75, help_text="Minimum floor price percent (e.g. 75 means min 75% of base price)")
    ai_max_discount_percent = models.IntegerField(default=20, help_text="Maximum discount % AI is permitted to negotiate")
    ai_negotiation_strategy = models.CharField(max_length=50, default='balanced', help_text="conservative | balanced | high_conversion")
    ai_negotiation_instructions = models.TextField(blank=True, default="Offer complimentary side makeups first. If client asks for discount, offer 10% then up to 20% max with today-only urgency.")

    class Meta:
        verbose_name = 'Site Settings'

    def __str__(self):
        return 'Site Settings'


class Artist(models.Model):
    SPECIALITY_CHOICES = [
        ('makeup', 'Makeup'),
        ('hair', 'Hair'),
        ('nails', 'Nails'),
        ('beauty', 'Beauty & Skin'),
        ('all', 'All Services'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    photo = models.ImageField(upload_to='artists/', blank=True, null=True)
    bio = models.TextField(blank=True)
    specialities = models.CharField(max_length=200, default='makeup', help_text='Comma separated: makeup,hair,nails,beauty')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_specialities_list(self):
        return [s.strip() for s in self.specialities.split(',')]


class AcademyCourse(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=300, blank=True)
    duration_days = models.IntegerField(default=28)
    duration_label = models.CharField(max_length=50, default='4 Weeks')
    hours_per_day = models.IntegerField(default=3)
    total_hours = models.IntegerField(default=84)
    course_fee = models.DecimalField(max_digits=10, decimal_places=2, default=30000)
    gst_percent = models.IntegerField(default=18)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    batch_start_note = models.CharField(max_length=200, blank=True, default='Last Batch of 2026 — Starts 27th July')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def gst_amount(self):
        return round(float(self.course_fee) * self.gst_percent / 100)

    @property
    def total_payable(self):
        return float(self.course_fee) + self.gst_amount


class CourseModule(models.Model):
    course = models.ForeignKey(AcademyCourse, on_delete=models.CASCADE, related_name='modules')
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class MakeupPackage(models.Model):
    PACKAGE_TYPE = [
        ('bridal', 'Bridal Suite'),
        ('engagement', 'Engagement & Roka'),
        ('reception', 'Reception & Sangeet'),
        ('side_makeup', 'Side & Family Makeup'),
        ('party', 'Party & Festive Glam'),
        ('hair', 'Haute Hair Couture'),
        ('nails', 'Nails & Extensions'),
        ('beauty', 'Skin & Pre-Bridal'),
        ('custom', 'Custom Package'),
    ]
    name = models.CharField(max_length=200)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE, default='bridal')
    tagline = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Leave blank for "On Request"')
    display_label = models.CharField(max_length=60, blank=True, null=True, help_text='Clean human-friendly label e.g. Bridal Sangeet Makeup')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Original MRP for strikethrough display')
    features = models.TextField(help_text='One feature per line')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    # AI Negotiation & Admin Floor Pricing Guardrails
    min_negotiated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Absolute minimum price AI Concierge is allowed to offer')
    max_discount_percent = models.IntegerField(default=15, help_text='Maximum discount percentage AI is permitted to negotiate')
    allow_ai_negotiation = models.BooleanField(default=True, help_text='Allow AI Concierge to negotiate on this package')

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def price_label(self):
        if self.price:
            return f"₹{int(self.price):,}"
        return 'On Request'

    @property
    def human_label(self):
        if self.display_label and self.display_label.strip():
            return self.display_label.strip()
        type_map = {
            'bridal': 'Bridal Makeup',
            'engagement': 'Engagement & Roka',
            'reception': 'Reception & Sangeet',
            'side_makeup': 'Side & Family Makeup',
            'party': 'Party & Festive Glam',
            'hair': 'Haute Hair Couture',
            'nails': 'Nails & Extensions',
            'beauty': 'Pre-Bridal Skincare',
            'custom': 'Bespoke Package',
        }
        return type_map.get(self.package_type, self.name)

    def get_features_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('bridal', 'Bridal'),
        ('engagement', 'Engagement'),
        ('reception', 'Reception'),
        ('hair', 'Hair'),
        ('nails', 'Nails'),
        ('beauty', 'Beauty'),
        ('party', 'Party'),
        ('academy', 'Academy'),
    ]
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='bridal')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    instagram_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Person / Lookbook Grouping (Avoid repeating same person, enable grouped lookbook modal)
    look_group_id = models.CharField(max_length=50, blank=True, help_text='ID to group multiple photos of the same bride/person e.g. "bengali_bride"')
    look_group_name = models.CharField(max_length=150, blank=True, help_text='Title for lookbook e.g. "Royal Bengali Bride (4 Looks)"')
    is_group_cover = models.BooleanField(default=True, help_text='Primary card shown on main grid')

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.caption or f"Gallery Image {self.id}"


class MediaItem(models.Model):
    """Admin-manageable Photos, Instagram Reels/Posts, and YouTube Videos"""
    MEDIA_TYPES = [
        ('image', 'Uploaded Photo / Image'),
        ('instagram', 'Instagram Post / Reel (Auto-Embed)'),
        ('youtube', 'YouTube Video (Auto-Embed)'),
        ('video_file', 'Direct Video File (Muted/Music MP4)'),
    ]
    CATEGORY_CHOICES = [
        ('bridal', 'Bridal Suite'),
        ('engagement', 'Engagement & Roka'),
        ('reception', 'Reception & Sangeet'),
        ('hair', 'Haute Hair'),
        ('nails', 'Nail Extensions & Art'),
        ('beauty', 'Skin & Pre-Bridal'),
        ('party', 'Party Glam'),
        ('academy', 'Academy Masterclass'),
    ]
    SECTION_CHOICES = [
        ('gallery', 'Gallery Showcase'),
        ('reels', 'Bridal Reels & Motion'),
        ('both', 'Both Gallery & Reels'),
    ]

    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='bridal')
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='gallery')
    caption = models.TextField(blank=True)
    
    # Uploaded image or video thumbnail
    image_file = models.ImageField(upload_to='media_uploads/images/', blank=True, null=True)
    video_file = models.FileField(upload_to='media_uploads/videos/', blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    
    # External URLs
    external_url = models.URLField(max_length=500, blank=True, help_text='Instagram post/reel URL or YouTube link')
    embed_code = models.TextField(blank=True, help_text='Generated or custom embed code / video ID')
    views_count = models.CharField(max_length=50, blank=True, default='25.4K+ views')
    
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"[{self.get_media_type_display()}] {self.title}"

    @property
    def display_thumb(self):
        if self.image_file:
            return self.image_file.url
        if self.thumbnail_url:
            return self.thumbnail_url
        if self.media_type == 'youtube' and self.embed_code:
            return f"https://img.youtube.com/vi/{self.embed_code}/hqdefault.jpg"
        return '/static/core/images/anshita_front.jpg'


class ServicePrice(models.Model):
    """Admin-controllable prices for each service type"""
    SERVICE_CHOICES = [
        ('makeup_basic', 'Makeup - Basic'),
        ('makeup_hd', 'Makeup - HD Bridal'),
        ('makeup_airbrush', 'Makeup - Airbrush Bridal'),
        ('hair_basic', 'Hair - Basic Styling'),
        ('hair_bridal', 'Hair - Bridal'),
        ('nails_basic', 'Nails - Basic Manicure'),
        ('nails_art', 'Nails - Nail Art'),
        ('nails_extension', 'Nails - Extension'),
        ('beauty_facial', 'Beauty - Facial'),
        ('beauty_prebridal', 'Beauty - Pre-Bridal Package'),
        ('tejal_makeup', 'Tejal - Makeup Package'),
        ('shristee_nails', 'Shristee - Nail Art Package'),
    ]
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_label = models.CharField(max_length=100, blank=True, help_text='Override display e.g. "Starting ₹1,500"')
    is_on_request = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_service_display()} — ₹{self.price}"

    def display_price(self):
        if self.is_on_request:
            return 'On Request'
        if self.price_label:
            return self.price_label
        return f'₹{int(self.price):,}'


class EventPackage(models.Model):
    CATEGORY_CHOICES = [
        ('photography', '📸 Photography & Cinematography'),
        ('decor', '🎪 Event Planning & Stage Decor'),
        ('catering', '🍽️ Catering & Hospitality'),
        ('salon', '💆 Salon & Pre-Bridal Care'),
        ('dj', '🎶 DJ, Sound & Entertainment'),
        ('full_event', '👑 Full Wedding Management'),
        ('custom', '✨ Custom VIP Partner Add-on'),
    ]
    PACKAGE_TYPE = [
        ('photography_premium', 'Photography - Premium'),
        ('photography_standard', 'Photography - Standard'),
        ('full_event', 'Full Event Management'),
        ('custom', 'Custom Package'),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='custom')
    package_type = models.CharField(max_length=30, choices=PACKAGE_TYPE, default='custom')
    description = models.TextField(blank=True)
    vendor_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0.00, help_text='Base external vendor cost charged to studio')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Client quote price')
    price_label = models.CharField(max_length=100, default='On Request')
    features = models.TextField(help_text='One feature per line', blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_features_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    @property
    def studio_commission(self):
        if self.price and self.vendor_cost is not None:
            return max(0.0, float(self.price) - float(self.vendor_cost))
        return 0.0

    @property
    def margin_percent(self):
        if self.price and float(self.price) > 0 and self.vendor_cost is not None:
            comm = float(self.price) - float(self.vendor_cost)
            return round((comm / float(self.price)) * 100, 1)
        return 0.0

    @property
    def roi_percent(self):
        if self.vendor_cost and float(self.vendor_cost) > 0 and self.price:
            comm = float(self.price) - float(self.vendor_cost)
            return round((comm / float(self.vendor_cost)) * 100, 1)
        return 0.0

    def display_price(self):
        if self.price:
            p = int(self.price)
            if p >= 100000:
                lakh = p / 100000
                return f'₹{lakh:.1f} Lakh' if lakh != int(lakh) else f'₹{int(lakh)} Lakh'
            return f'₹{p:,}'
        return self.price_label


class ChatMessage(models.Model):
    session_id = models.CharField(max_length=100)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat {self.session_id[:8]} - {self.created_at.strftime('%d %b %Y')}"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    reset_token = models.CharField(max_length=100, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Admin: {self.user.username}"


class CustomerReview(models.Model):
    client_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100, default='Royal Bride')
    location = models.CharField(max_length=100, blank=True, default='India')
    rating = models.IntegerField(default=5)  # 1 to 5
    review_text = models.TextField()
    wedding_date = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=True)
    avatar_url = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.client_name} ({self.rating}★) - {self.event_type}"

    def get_stars_range(self):
        return range(self.rating)


class StudioService(models.Model):
    """Admin-controllable signature service disciplines rendered in #services"""
    CATEGORY_CHOICES = [
        ('bridal', 'Bridal Suite'),
        ('reception', 'Reception & Cocktail'),
        ('engagement', 'Engagement & Roka'),
        ('sangeet', 'Sangeet & Haldi'),
        ('saree', 'Haute Hair & Saree Draping'),
        ('party', 'Family & Bridesmaids'),
        ('nails', 'Nail Extensions & Art'),
        ('beauty', 'Skin & Pre-Bridal'),
    ]
    title = models.CharField(max_length=200, help_text='Service title e.g. "Imperial Bridal Couture & Airbrush"')
    discipline = models.CharField(max_length=150, help_text='Discipline tag e.g. "SIGNATURE DISCIPLINE 01 · SACRED WEDDING DAY"')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='bridal')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Actual standalone service investment in ₹')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Optional standard discounted price in ₹')
    bundle_note = models.CharField(max_length=200, blank=True, help_text='Short optional bundle tag e.g. "Save 25% with Wedding Package"')
    description = models.TextField(help_text='Concise 1-2 sentence luxury editorial description')
    features = models.TextField(help_text='Features/inclusions list, one feature per line for dynamic admin control', blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, help_text='Static or CDN fallback path e.g. "/static/core/images/curated/..."')
    look_group_id = models.CharField(max_length=100, blank=True, help_text='Linked look group ID for lookbook popup')
    
    # AI Negotiation & Admin Floor Pricing Guardrails
    min_negotiated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Absolute minimum price AI is allowed to negotiate for this service')
    max_discount_percent = models.IntegerField(default=15, help_text='Max discount % AI is permitted to negotiate for this service')
    allow_ai_negotiation = models.BooleanField(default=True, help_text='Allow AI Concierge to negotiate on this service')

    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"[{self.discipline}] {self.title}"

    def get_features_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return '/static/core/images/curated/royal_crimson_bride_angle3.jpg'


class LookGroup(models.Model):
    """Categorized person/client folder for photos, videos, Instagram reels, and YouTube embeds"""
    CATEGORY_CHOICES = [
        ('bridal', 'Bridal Suites'),
        ('reception', 'Reception & Cocktail'),
        ('engagement', 'Engagement & Roka'),
        ('sangeet', 'Sangeet & Haldi'),
        ('hair', 'Hair & Draping'),
        ('party', 'Party & Side Glam'),
        ('nails', 'Nail Artistry'),
        ('studio', 'Studio & Masterclass'),
    ]
    name = models.CharField(max_length=200, help_text='Group display name e.g. "Kuhu — Traditional Kolkata Banarasi & Chandan Art"')
    client_name = models.CharField(max_length=100, blank=True, help_text='Client or Model name e.g. "Kuhu", "Miss Rajak"')
    makeup_type = models.CharField(max_length=150, blank=True, help_text='Type of makeup e.g. "Traditional Bengali Mukut & Chandan", "Mauve Shimmer Cut-Crease"')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='bridal')
    slug = models.SlugField(max_length=150, blank=True, help_text='URL-friendly identifier e.g. "kuhu-banarasi-bride"')
    cover_image = models.ImageField(upload_to='lookgroups/covers/', blank=True, null=True)
    cover_image_url = models.CharField(max_length=500, blank=True, help_text='Fallback static image path')
    description = models.TextField(blank=True)
    show_external_link_button = models.BooleanField(default=True, help_text='Allow visitors to see "Watch on Instagram / YouTube" buttons for this album')
    is_featured = models.BooleanField(default=False, help_text='Display in top spatial 3D card fan')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        client = f" ({self.client_name})" if self.client_name else ""
        return f"{self.name}{client}"

    @property
    def display_cover(self):
        if self.cover_image:
            return self.cover_image.url
        if self.cover_image_url:
            return self.cover_image_url
        first_item = self.media_items.filter(order__gte=0).first()
        if first_item:
            return first_item.display_thumb
        return '/static/core/images/curated/royal_crimson_bride_angle3.jpg'

    @property
    def photo_count(self):
        return self.media_items.filter(media_type='image').count()

    @property
    def video_count(self):
        return self.media_items.exclude(media_type='image').count()

    @property
    def count_summary(self):
        p = self.photo_count
        v = self.video_count
        parts = []
        if p > 0:
            parts.append(f"{p} Photo{'s' if p > 1 else ''}")
        if v > 0:
            parts.append(f"{v} Video{'s' if v > 1 else ''}")
        return " · ".join(parts) if parts else "Portfolio Look"


class LookMediaItem(models.Model):
    """Individual photo, video file, Instagram post/reel, or YouTube link inside a LookGroup"""
    MEDIA_TYPES = [
        ('image', 'Uploaded Photo'),
        ('video_file', 'Direct Video File (MP4)'),
        ('instagram', 'Instagram Reel / Post (Auto Embed)'),
        ('youtube', 'YouTube Video (Auto Embed)'),
    ]
    group = models.ForeignKey(LookGroup, on_delete=models.CASCADE, related_name='media_items')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')
    image_file = models.ImageField(upload_to='lookgroups/media/', blank=True, null=True)
    video_file = models.FileField(upload_to='lookgroups/videos/', blank=True, null=True)
    external_url = models.URLField(max_length=500, blank=True, help_text='Instagram Reel/Post or YouTube URL')
    embed_code = models.CharField(max_length=200, blank=True, help_text='Instagram shortcode or YouTube video ID')
    thumbnail_url = models.CharField(max_length=500, blank=True, help_text='Auto-fetched thumbnail for Instagram/YouTube or static path')
    title = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    show_platform_link = models.BooleanField(default=True, help_text='Show "Open in Instagram/YouTube" badge for this item')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"[{self.get_media_type_display()}] {self.title or self.caption or f'Item {self.id}'} in {self.group.name}"

    @property
    def display_thumb(self):
        if self.image_file:
            return self.image_file.url
        if self.thumbnail_url:
            return self.thumbnail_url
        if self.media_type == 'youtube' and self.embed_code:
            return f"https://img.youtube.com/vi/{self.embed_code}/hqdefault.jpg"
        return '/static/core/images/curated/royal_crimson_bride_angle3.jpg'


