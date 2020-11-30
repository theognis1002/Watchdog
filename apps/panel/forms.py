from django import forms
from django.core.exceptions import ValidationError

from .models import WatchdogMetaDetails


class AddProductForm(forms.Form):
    product_url = forms.URLField(
        label="", widget=forms.TextInput(attrs={"placeholder": "Product URL"})
    )


class WatchdogMetaDetailsForm(forms.ModelForm):
    slack_api_key = forms.CharField(label="Slack API token", max_length=255)
    slack_webhook_uri = forms.CharField(label="Slack Webhook URI", max_length=255)
    slack_channel_id = forms.CharField(label="Slack Channel ID#", max_length=55)
    slack_private_channel_ids = forms.CharField(
        label="Slack Private Channel ID#'s",
        help_text="Separate channels by comma with no spaces (ie; GXO628C90,HB9628C90)",
        max_length=55,
    )

    def clean_slack_private_channel_ids(self):
        data = self.cleaned_data["slack_private_channel_ids"]
        if len(data) > 10 and "," not in data:
            raise ValidationError("Please separate by channels by commas")

        return data

    class Meta:
        model = WatchdogMetaDetails
        fields = (
            "slack_api_key",
            "slack_webhook_uri",
            "slack_channel_id",
            "slack_private_channel_ids",
        )
