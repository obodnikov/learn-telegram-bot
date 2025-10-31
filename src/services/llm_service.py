"""LLM Service for interacting with OpenRouter API."""

from typing import Dict, Any, List, Optional
import json
import httpx
from src.utils.logger import get_logger
from src.utils.exceptions import LLMServiceError

logger = get_logger(__name__)


class LLMService:
    """Service for interacting with OpenRouter API."""

    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize LLM service.

        Args:
            api_key: OpenRouter API key
            model: Model identifier
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/learn-telegram-bot",
            "X-Title": "Telegram Learning Bot"
        }
        logger.info(f"LLMService initialized with model: {model}")

    async def generate_questions(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> List[Dict[str, Any]]:
        """
        Generate questions using LLM.

        Args:
            prompt: Formatted prompt for question generation
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            List of generated questions

        Raises:
            LLMServiceError: If API call fails
        """
        logger.info("Generating questions with LLM...")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )

                if response.status_code != 200:
                    error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise LLMServiceError(error_msg)

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse and validate response
                questions = await self.validate_response(content)

                logger.info(f"Successfully generated {len(questions)} questions")
                return questions

        except httpx.TimeoutException as e:
            error_msg = f"OpenRouter API timeout: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)
        except httpx.HTTPError as e:
            error_msg = f"OpenRouter HTTP error: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)
        except KeyError as e:
            error_msg = f"Unexpected API response format: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)
        except Exception as e:
            error_msg = f"LLM service error: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)

    async def validate_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Validate and parse LLM response.

        Expected format is JSON array of questions with fields:
        - question_text
        - choice_a, choice_b, choice_c, choice_d
        - correct_answer (A/B/C/D)
        - explanation
        - difficulty
        - tags (optional)

        Args:
            response: Raw LLM response

        Returns:
            Parsed and validated questions

        Raises:
            LLMServiceError: If response is invalid
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()

            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]

            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            # Parse JSON
            questions = json.loads(response)

            if not isinstance(questions, list):
                raise LLMServiceError("Response must be a JSON array of questions")

            # Validate each question
            validated_questions = []
            required_fields = [
                "question_text", "choice_a", "choice_b", "choice_c", "choice_d",
                "correct_answer", "explanation", "difficulty"
            ]

            for i, q in enumerate(questions):
                if not isinstance(q, dict):
                    logger.warning(f"Question {i} is not a dictionary, skipping")
                    continue

                # Check required fields
                missing_fields = [field for field in required_fields if field not in q]
                if missing_fields:
                    logger.warning(
                        f"Question {i} missing fields: {missing_fields}, skipping"
                    )
                    continue

                # Validate correct_answer
                if q["correct_answer"].upper() not in ["A", "B", "C", "D"]:
                    logger.warning(
                        f"Question {i} has invalid correct_answer: {q['correct_answer']}, skipping"
                    )
                    continue

                # Normalize correct_answer to uppercase
                q["correct_answer"] = q["correct_answer"].upper()

                # Validate difficulty
                valid_difficulties = ["beginner", "intermediate", "advanced", "expert"]
                if q["difficulty"].lower() not in valid_difficulties:
                    logger.warning(
                        f"Question {i} has invalid difficulty: {q['difficulty']}, defaulting to 'intermediate'"
                    )
                    q["difficulty"] = "intermediate"

                # Ensure tags is a list
                if "tags" not in q:
                    q["tags"] = []
                elif not isinstance(q["tags"], list):
                    q["tags"] = [str(q["tags"])]

                validated_questions.append(q)

            if not validated_questions:
                raise LLMServiceError("No valid questions found in response")

            logger.info(f"Validated {len(validated_questions)} questions")
            return validated_questions

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse LLM response as JSON: {e}\nResponse: {response[:200]}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)
        except Exception as e:
            error_msg = f"Response validation error: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)

    async def test_connection(self) -> bool:
        """
        Test connection to OpenRouter API.

        Returns:
            True if connection successful

        Raises:
            LLMServiceError: If connection test fails
        """
        logger.info("Testing OpenRouter connection...")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a connection test. Please respond with 'OK'."
                }
            ],
            "max_tokens": 10
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )

                if response.status_code == 200:
                    logger.info("OpenRouter connection successful")
                    return True
                else:
                    error_msg = f"OpenRouter connection failed: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise LLMServiceError(error_msg)

        except httpx.TimeoutException as e:
            error_msg = f"OpenRouter connection timeout: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)
        except httpx.HTTPError as e:
            error_msg = f"OpenRouter connection HTTP error: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)
        except Exception as e:
            error_msg = f"OpenRouter connection test failed: {e}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg)
