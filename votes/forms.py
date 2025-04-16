from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from .models import CategoryChoices, Poll, PollOption


class PollCreationForm(forms.ModelForm):
    ALLOWED_IMAGE_TYPES = ["image/jpg", "image/jpeg", "image/png"]

    MAX_IMAGE_SIZE = 2 * pow(1024, 2)  # MB to B(bytes)

    cover = forms.ImageField(
        required=False,
        label="Poll Cover (Optional)",
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])],
        widget=forms.FileInput(
            attrs={"class": "file-input", "accept": "image/*", "id": "cover"}
        ),
    )

    is_public = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "switch-input"}),
        label="Visibility",
        help_text="Make this public when turned on, and private else",
    )

    is_anonymous = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "switch-input"}),
        label="Anonymous Voting",
        help_text="Hide voter identities",
    )

    results_visible = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "switch-input"}),
        label="Show Results",
        help_text="Allow voters to see results",
    )

    end_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="End Date",
        help_text="Set when this poll should be closed",
    )

    max_votes = forms.IntegerField(
        required=False,
        label="Max Votes",
        help_text="Limit total votes (leave blank for unlimited)",
        widget=forms.NumberInput(attrs={"placeholder": "Unlimited"}),
        min_value=1,
    )

    class Meta:
        model = Poll
        fields = [
            "cover",
            "title",
            "description",
            "category",
            "is_public",
            "is_anonymous",
            "results_visible",
            "end_at",
            "max_votes",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter your poll question",
                    "required": "",
                    "id": "text",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "id": "description",
                    "rows": "4",
                    "placeholder": "Add more details about your poll",
                }
            ),
            "category": forms.Select(
                attrs={"id": "category", "required": ""},
                choices=CategoryChoices.choices,
            ),
        }

    def clean_cover(self):
        cover = self.cleaned_data.get("cover")

        if cover:
            if cover.content_type not in self.ALLOWED_IMAGE_TYPES:
                raise ValidationError(
                    "Please, the extension need to be jpg, png, or jped."
                )

            if cover.size > self.MAX_IMAGE_SIZE:
                raise ValidationError("This image is too big, it's above 5MB")
        return cover

    def clean_category(self):
        category = self.cleaned_data.get("category")

        for c in CategoryChoices.choices:
            if c[0] == category:
                return category
        raise ValidationError("Invalid category")

    def clean_end_at(self):
        end_at = self.cleaned_data.get("end_at")

        if end_at and end_at < timezone.now():
            raise ValidationError("Invalid end date")
        return end_at

    def clean_max_votes(self):
        max_votes = self.cleaned_data.get("max_votes")

        if max_votes:
            try:
                max_votes = int(max_votes)
            except:
                raise ValidationError("Invalid number")

        return max_votes


class PollOptionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        options = kwargs.pop("options", None)
        super().__init__(*args, **kwargs)

        if options:
            for i, option in enumerate(options, start=1):
                self.fields[f"option{i}"] = forms.CharField(
                    initial=option,
                    widget=forms.TextInput(
                        attrs={
                            "placeholder": f"Option {i}",
                            "required": "required",
                            "name": f"option{i}",
                        }
                    ),
                )
        else:
            for i in range(1, 3):
                self.fields[f"option{i}"] = forms.CharField(
                    widget=forms.TextInput(
                        attrs={
                            "placeholder": f"Option {i}",
                            "required": "",
                            "name": f"option{i}",
                        }
                    )
                )

    def get_options(self, data):
        options = []

        for k, v in data.items():
            if k.startswith("option") and data.get(k):
                options.append(v)

        return options
