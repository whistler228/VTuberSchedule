from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.forms import CharField
from django.core.exceptions import ValidationError
from .models import CustomUser
from scrape.getChannel import get_subbed_channel

import requests


class CustomForm(UserCreationForm):
    channel_id = CharField(required=True,
                           label="チャンネルID",
                           error_messages={"invalid": "不正なIDです。",
                                           "exist": "既に存在します。"})
    nickname = CharField(required=True, max_length=12, label="ニックネーム")
    email = CharField(required=False, max_length=254, label="メールアドレス")

    class Meta:
        model = CustomUser
        fields = ("username", "channel_id", "nickname", "email", "password1", "password2")

    def save(self, commit=True):
        cleaned_data = super(CustomForm, self).clean()
        if self.errors:
            return self.errors
        user = super(CustomForm, self).save(commit=False)
        user.channel_id = cleaned_data["channel_id"]
        user.nickname = cleaned_data["nickname"]
        if commit:
            user.save()
        return user

    def clean_channel_id(self):
        if CustomUser.objects.filter(channel_id=self.cleaned_data["channel_id"]):
            raise ValidationError(self.fields["channel_id"].error_messages["exist"])
        if len(self.cleaned_data["channel_id"]) > 24:
            raise ValidationError(self.fields["channel_id"].error_messages["invalid"])
        res = requests.get(f"https://www.youtube.com/channel/{self.fields['channel_id']}")
        if not res.status_code == 200:
            raise ValidationError(self.fields["channel_id"].error_messages["invalid"])
        return self.cleaned_data["channel_id"]

    def clean_nickname(self):
        if not self.cleaned_data["nickname"]:
            raise ValidationError("Please Enter your nickname.")
        if len(self.cleaned_data["nickname"]) > 12:
            raise ValidationError("Nickname must be <= 12 char.")
        return self.cleaned_data["nickname"]


class SignUp(generic.CreateView):
    form_class = CustomForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"
