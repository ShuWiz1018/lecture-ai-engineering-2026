"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 会話モード

ツールを持たない「素の」呼び出し。会話モードでは、同じ実行中の質問履歴を保つ。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    _print_usage(response)
    return response.text


def _print_usage(response) -> None:
    usage = response.usage_metadata
    if usage is not None:
        print(
            f"[トークン数] 入力: {usage.prompt_token_count}, "
            f"出力: {usage.candidates_token_count}"
        )


def interactive_chat() -> None:
    client = genai.Client(api_key=get_api_key())
    conversation = client.chats.create(model=MODEL)

    print("質問を入力してください。終了するには exit または quit と入力します。")
    while True:
        try:
            question = input("質問> ").strip()
        except EOFError:
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        response = conversation.send_message(question)
        _print_usage(response)
        print(f"回答> {response.text}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        if args.question is None:
            interactive_chat()
        else:
            print(f"[質問] {args.question}\n")
            print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
