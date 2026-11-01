"""Công cụ mặc định cho ngôn ngữ có khoảng trắng và không cần đổi chữ cho giọng AI (tiếng Anh, Tây Ban Nha, Pháp...)."""
import re


def display(s):
    return s


def speak(s):
    return s


def words(text):
    text = re.sub(r"(?<=\d)[.,](?=\d)", "", text.lower()).replace("-", " ")
    return re.findall(r"\w+", text)


def count(s):
    return len(s.split())
