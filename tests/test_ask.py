from types import SimpleNamespace

from app import ask


def test_interactive_chat_reuses_conversation(monkeypatch, capsys):
    class FakeConversation:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(text=f"回答: {question}", usage_metadata=None)

    class FakeChats:
        def __init__(self):
            self.conversation = FakeConversation()
            self.models = []

        def create(self, *, model):
            self.models.append(model)
            return self.conversation

    chats = FakeChats()
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask.genai, "Client", lambda **kwargs: SimpleNamespace(chats=chats))
    questions = iter(["LoRAとは？", "それは何に使うの？", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask.interactive_chat()

    assert chats.models == [ask.MODEL]
    assert chats.conversation.questions == ["LoRAとは？", "それは何に使うの？"]
    assert "回答: それは何に使うの？" in capsys.readouterr().out