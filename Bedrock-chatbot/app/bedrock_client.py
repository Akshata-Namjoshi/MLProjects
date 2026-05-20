import json
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, Generator

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from .config import AWS_REGION, BEDROCK_INFERENCE_PROFILE_ARN, BEDROCK_PROMPT_ARN, MAX_TOKENS, MAX_RETRIES, BASE_TEMPERATURE

_executor = ThreadPoolExecutor(max_workers=8)

def _get_bedrock_runtime():
    return boto3.client('bedrock-runtime', region_name=AWS_REGION)

def _invoke_bedrock(
    user_message: str,
    temperature: float,
    stream: bool = False,
)-> Dict[str, Any]:
    
    """
    Synchronous invocation of Bedrock via an inference profile and a managed prompt.
    """
    
    bedrock = _get_bedrock_runtime()

    # Typical body for Claude-like text model – adjust for your chosen model
    body = {
        "inputText": user_message,
        "textGenerationConfig": {
            "temperature": temperature,
            "maxTokens": MAX_TOKENS,
        },
        "promptTemplate": {
            "promptArn": BEDROCK_PROMPT_ARN,
            # if your prompt has variables, supply here when supported
            # "promptVariables": {...}
        },
    }

    attempt = 0
    backoff = 0.5

    while True:
        try:
            resp = bedrock.invoke_model_with_response_stream(
                body=json.dumps(body),
                inferenceProfileArn=BEDROCK_INFERENCE_PROFILE_ARN,
                contentType="application/json",
                accept="application/json",
            )
            return resp

        except (BotoCoreError, ClientError) as e:
            attempt += 1
            if attempt > MAX_RETRIES:
                raise e
            time.sleep(backoff)
            backoff *= 2


def _parse_streaming_response(stream_resp) -> Generator[str, None, None]:
    """
    Parse streaming chunks into text tokens.
    """
    for event in stream_resp.get("body"):
        chunk = event.get("chunk")
        if not chunk:
            continue
        payload = json.loads(chunk.get("bytes").decode("utf-8"))
        token = payload.get("outputText") or payload.get("completion") or ""
        if token:
            yield token


def call_bedrock_async(
    user_message: str,
    temperature: float,
    stream: bool = False,
):
    """
    Submit a Bedrock call to run in a thread. Returns a Future or a generator.
    """

    if stream:
        # For streaming, wrap the synchronous call and yield tokens
        def _stream_gen():
            resp = _invoke_bedrock(user_message, temperature, stream=True)
            for token in _parse_streaming_response(resp):
                yield token

        return _stream_gen()

    # Non-streaming: run in executor
    return _executor.submit(_invoke_bedrock, user_message, temperature, False)