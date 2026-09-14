from django.db import models
from django.contrib.auth.models import User


class SiteSettings(models.Model):
    """Global site settings controllable by admin"""
    whatsapp_number = models.CharField(max_length=20, default='917879223442')
    instagram_url = models.URLField(default='https://www.instagram.com/anshitamakeover21/')
    
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
    price_label = models.CharField(max_length=100, default='On Request')
    features = models.TextField(help_text='One feature per line')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

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
    PACKAGE_TYPE = [
        ('photography_premium', 'Photography - Premium'),
        ('photography_standard', 'Photography - Standard'),
        ('full_event', 'Full Event Management'),
        ('custom', 'Custom Package'),
    ]
    name = models.CharField(max_length=200)
    package_type = models.CharField(max_length=30, choices=PACKAGE_TYPE, default='custom')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
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

