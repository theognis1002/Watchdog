from django import forms
from .models import WatchdogSettings


class AddProductForm(forms.Form):
    product_url = forms.URLField(
        label="", widget=forms.TextInput(attrs={"placeholder": "Product URL"})
    )


class WatchdogSettingsForm(forms.ModelForm):
    slack_api_key = forms.CharField(label="Slack API token", max_length=255)
    slack_webhook_uri = forms.CharField(label="Slack Webhook URI", max_length=255)
    slack_channel_id = forms.CharField(label="Slack Channel ID#", max_length=55)

    class Meta:
        model = WatchdogSettings
        fields = ("slack_api_key", "slack_webhook_uri", "slack_channel_id")
