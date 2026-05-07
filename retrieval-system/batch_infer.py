"""
批次推論：讀入 input.csv（欄位：題目），輸出 output.csv（欄位：題目, 答案）

用法：
    python batch_infer.py input.csv output.csv
"""
import argparse
import asyncio
import os
import sys

import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE, "src"))

from prompt_builder import build_system_prompt


def _make_async_client() -> openai.AsyncOpenAI:
    api_key = os.environ.get("TWCC_API_KEY")
    base_url = os.environ.get("TWCC_API_URL", "https://api-ams.twcc.ai/api") + "/models"
    timeout = float(os.environ.get("TWCC_TIMEOUT", "60"))
    max_retries = int(os.environ.get("TWCC_MAX_RETRY", "2"))
    if not api_key:
        raise RuntimeError("TWCC_API_KEY 未設定，請在 .env 中填入 API key。")
    return openai.AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
    )


async def _ask_async(
    client: openai.AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    question: str,
    system_prompt: str,
    model: str,
) -> str:
    async with semaphore:
        response = await client.chat.completions.create(
            model=model,
            max_tokens=300,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        )
    return response.choices[0].message.content


async def _process_all(questions: list[str], system_prompt: str) -> list[str]:
    client = _make_async_client()
    model = os.environ.get("TWCC_MODEL", "llama3.3-ffm-70b-16k-chat")
    concurrency = int(os.environ.get("TWCC_MAX_CONCURRENT", "10"))
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [_ask_async(client, semaphore, q, system_prompt, model) for q in questions]
    return await asyncio.gather(*tasks)


def main(input_path: str, output_path: str) -> None:
    print("載入課程資料...", end=" ", flush=True)
    system_prompt = build_system_prompt(os.path.join(_BASE, "data"))
    print("完成。")

    df = pd.read_csv(input_path)
    if "題目" not in df.columns:
        raise ValueError("input CSV 缺少「題目」欄位。")

    questions = df["題目"].tolist()
    concurrency = int(os.environ.get("TWCC_MAX_CONCURRENT", "10"))
    print(f"處理 {len(questions)} 題（最多 {concurrency} 題並行）...", end=" ", flush=True)

    answers = asyncio.run(_process_all(questions, system_prompt))
    print("完成。")

    df["答案"] = answers
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"輸出至 {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NLP 課程檢索系統 — 批次推論")
    parser.add_argument("input", help="input CSV 路徑（欄位：題目）")
    parser.add_argument("output", help="output CSV 路徑（欄位：題目, 答案）")
    args = parser.parse_args()
    main(args.input, args.output)
