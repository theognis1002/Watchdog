from django.db import models
from django.contrib.sites.models import Site


class WatchdogSettings(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    slack_api_key = models.CharField(max_length=255, blank=True)
    slack_webhook_uri = models.URLField(blank=True)
    slack_channel_id = models.CharField(max_length=55, blank=True)

    def __str__(self):
        return f"{self.site} settings"

    class Meta:
        verbose_name = "Watchdog Settings"
        verbose_name_plural = "Watchdog Settings"


class TargetSite(models.Model):
    site_name = models.CharField(max_length=255)
    base_url = models.URLField()

    def __str__(self):
        return self.site_name


class Product(models.Model):
    name = models.CharField(max_length=255, blank=True)
    price = models.FloatField(blank=True, null=True)
    url = models.URLField()
    sku = models.CharField(max_length=255, blank=True)
    image = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)
    site = models.ForeignKey(TargetSite, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.price}"

    @property
    def add_to_cart_url(self):
        return self.url

    def save(self, *args, **kwargs):
        if "walmart.com" in self.url:
            site = TargetSite.objects.get(pk=1)
            self.site = site
        elif "amazon.com" in self.url:
            site = TargetSite.objects.get(pk=2)
            self.site = site
        elif "bestbuy.com" in self.url:
            site = TargetSite.objects.get(pk=2)
            self.site = site
        elif "target.com" in self.url:
            site = TargetSite.objects.get(pk=2)
            self.site = site
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Products"
        verbose_name_plural = "Products"


class ProductReleaseHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.timestamp}"

    class Meta:
        verbose_name = "Product Release History"
        verbose_name_plural = "Product Release History"