from google.cloud import translate_v2 as translate

class GoogleTranslator:
    def __init__(self):
        self.client = translate.Client()

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        result = self.client.translate(text, source_language=source_lang, target_language=target_lang, format_='text')
        return result["translatedText"]