"""第1回: 素のLLMに会話形式で質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 既定の質問から会話を始める

ツールは持たない「素の」呼び出しだが、同じチャットの中で会話履歴を保つ。
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


def ask(question: str, chat=None) -> str:
    """質問を送り、回答を返す。chat を渡すとその会話履歴を引き継ぐ。"""
    client = genai.Client(api_key=get_api_key())
    chat = chat or client.chats.create(model=MODEL)
    response = chat.send_message(question)

    usage = response.usage_metadata
    print(
        f"[usage] 入力トークン数: {usage.prompt_token_count}, "
        f"出力トークン数: {usage.candidates_token_count}"
    )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)
        question = args.question
        while True:
            print(f"[質問] {question}\n")
            print(ask(question, chat))
            try:
                question = input("\n次の質問（空入力または exit で終了）> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not question or question.casefold() in {"exit", "quit"}:
                break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
