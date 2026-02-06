from contextvars import ContextVar
from typing import Dict, Any

# Context variable to store current language
current_language: ContextVar[str] = ContextVar("current_language", default="en")

TRANSLATIONS = {
    "en": {
        "ID": "ID",
        "Username": "Username",
        "Full Name": "Full Name",
        "Code": "Code",
        "Name": "Name",
        "Type": "Type",
        "User ID": "User ID",
        "Asset ID": "Asset ID",
        "Quantity": "Quantity",
        "Avg Cost": "Avg Cost",
        "Date": "Date",
        "Price": "Price",
        "User": "User",
        "Asset": "Asset",
        "Portfolio": "Portfolio",
        "Price History": "Price History",
        "Users": "Users",
        "Assets": "Assets",
        "Portfolios": "Portfolios",
        "Price Histories": "Price Histories"
    },
    "tr": {
        "ID": "ID",
        "Username": "Kullanıcı Adı",
        "Full Name": "Tam Ad",
        "Code": "Kod",
        "Name": "Ad",
        "Type": "Tip",
        "User ID": "Kullanıcı ID",
        "Asset ID": "Varlık ID",
        "Quantity": "Adet",
        "Avg Cost": "Ort. Maliyet",
        "Date": "Tarih",
        "Price": "Fiyat",
        "User": "Kullanıcı",
        "Asset": "Varlık",
        "Portfolio": "Portföy",
        "Price History": "Fiyat Geçmişi",
        "Users": "Kullanıcılar",
        "Assets": "Varlıklar",
        "Portfolios": "Portföyler",
        "Price Histories": "Fiyat Geçmişleri"
    }
}

class LazyString:
    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        lang = current_language.get()
        return TRANSLATIONS.get(lang, {}).get(self.key, self.key)
    
    def __repr__(self):
        return str(self)
