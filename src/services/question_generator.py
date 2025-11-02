"""Question generator service for creating questions using LLM."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from src.utils.logger import get_logger
from src.utils.exceptions import QuestionGenerationError, ConfigurationError
from src.services.llm_service import LLMService
from src.services.example_parser import ExampleParser, ExampleQuestion
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class QuestionGenerator:
    """Generate questions using LLM with optional examples."""

    def __init__(
        self,
        llm_service: LLMService,
        config_loader: ConfigLoader,
        example_parser: ExampleParser,
        repository = None
    ):
        """
        Initialize question generator.

        Args:
            llm_service: LLM service instance
            config_loader: Configuration loader instance
            example_parser: Example parser instance
            repository: Optional repository for checking existing questions
        """
        self.llm_service = llm_service
        self.config_loader = config_loader
        self.example_parser = example_parser
        self.repository = repository
        logger.info("QuestionGenerator initialized")

    async def generate_questions(
        self,
        topic_id: str,
        count: int,
        db_topic_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate questions for a topic.

        Args:
            topic_id: Topic identifier
            count: Number of questions to generate

        Returns:
            List of generated questions

        Raises:
            QuestionGenerationError: If generation fails
        """
        logger.info(f"Generating {count} questions for topic: {topic_id}")

        try:
            # Get topic configuration
            topic_config = self.config_loader.get_topic(topic_id)
            if not topic_config:
                raise ConfigurationError(f"Topic not found: {topic_id}")

            # Check if topic has examples
            examples_config = getattr(topic_config, 'examples', None)

            if not examples_config:
                # No examples: standard generation
                logger.info(f"Standard generation mode (no examples) for topic: {topic_id}")
                return await self._generate_standard(topic_config, count)

            # Load example file
            example_file = examples_config.get("file") if isinstance(examples_config, dict) else getattr(examples_config, 'file', None)
            if not example_file:
                raise ConfigurationError(f"Missing 'file' in examples config for topic: {topic_id}")

            # Resolve example file path
            # If path already includes config/examples, use as-is; otherwise prepend it
            if example_file.startswith("config/examples/"):
                example_path = Path(example_file)
            else:
                example_path = Path("config/examples") / example_file
            examples = self.example_parser.load_examples(str(example_path))

            # Filter out examples that are already in the database (for hybrid mode)
            if self.repository and db_topic_id:
                existing_questions = self.repository.get_questions_for_topic(db_topic_id)
                examples = self.example_parser.filter_unused_examples(examples, existing_questions)

            # Get generation mode
            mode = examples_config.get("mode", "augment") if isinstance(examples_config, dict) else getattr(examples_config, 'mode', "augment")
            use_ratio = examples_config.get("use_ratio", 0.3) if isinstance(examples_config, dict) else getattr(examples_config, 'use_ratio', 0.3)

            # Generate based on mode
            if mode == "standard":
                return await self._generate_standard(topic_config, count, db_topic_id)
            elif mode == "augment":
                return await self._generate_augmented(topic_config, examples, count, db_topic_id)
            elif mode == "template":
                return await self._generate_templated(topic_config, examples, count, db_topic_id)
            elif mode == "hybrid":
                return await self._generate_hybrid(topic_config, examples, count, use_ratio, db_topic_id)
            else:
                raise ConfigurationError(f"Unknown generation mode: {mode}")

        except Exception as e:
            error_msg = f"Failed to generate questions for topic {topic_id}: {e}"
            logger.error(error_msg)
            if isinstance(e, (QuestionGenerationError, ConfigurationError)):
                raise
            raise QuestionGenerationError(error_msg)

    async def generate_questions_with_dedup(
        self,
        topic_id: str,
        count: int,
        db_topic_id: int = None,
        similarity_threshold: float = 0.85,
        duplicate_retry_threshold: float = 0.50,
        max_retries: int = 3,
        recent_context_limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Generate questions with enhanced duplicate detection and retry logic.

        This method extends the standard generation with:
        1. Fuzzy duplicate detection using similarity threshold
        2. Recent questions context for LLM (to avoid duplicates)
        3. Automatic retry if duplicate rate exceeds threshold

        Args:
            topic_id: Topic identifier
            count: Number of questions to generate
            db_topic_id: Database topic ID for duplicate checking
            similarity_threshold: Reject questions with >threshold similarity (0.0-1.0, default: 0.85)
            duplicate_retry_threshold: Retry if >threshold duplicates found (0.0-1.0, default: 0.50)
            max_retries: Maximum retry attempts (default: 3)
            recent_context_limit: Number of recent questions to show LLM (default: 20)

        Returns:
            List of generated unique questions

        Raises:
            QuestionGenerationError: If generation fails
        """
        if not self.repository or not db_topic_id:
            logger.warning(
                "Repository or db_topic_id not provided, falling back to standard generation"
            )
            return await self.generate_questions(topic_id, count, db_topic_id)

        logger.info(
            f"Enhanced generation for topic {topic_id}: count={count}, "
            f"similarity_threshold={similarity_threshold}, "
            f"duplicate_retry_threshold={duplicate_retry_threshold}, "
            f"max_retries={max_retries}"
        )

        # Get recent questions for LLM context
        recent_questions = self.repository.get_recent_questions(
            db_topic_id,
            limit=recent_context_limit
        )

        retry_count = 0
        all_unique_questions = []

        while retry_count <= max_retries:
            if retry_count > 0:
                logger.info(f"Retry attempt {retry_count}/{max_retries}")

            # Generate questions (with recent context if retry)
            if retry_count == 0:
                # First attempt: standard generation
                questions = await self.generate_questions(topic_id, count, db_topic_id)
            else:
                # Retry: inject stronger anti-duplicate prompt
                questions = await self._generate_with_anti_duplicate_context(
                    topic_id,
                    count - len(all_unique_questions),  # Only generate what we still need
                    recent_questions,
                    retry_count
                )

            # Check duplicates using fuzzy matching
            unique_questions = []
            duplicate_count = 0

            for question in questions:
                question_text = question.get("question_text", "")

                # Check fuzzy duplicate
                is_duplicate, similarity = self.repository.check_duplicate_question_fuzzy(
                    db_topic_id,
                    question_text,
                    threshold=similarity_threshold
                )

                if is_duplicate:
                    duplicate_count += 1
                    logger.debug(
                        f"Fuzzy duplicate detected (similarity={similarity:.2f}): "
                        f"{question_text[:50]}..."
                    )
                else:
                    unique_questions.append(question)

            # Calculate duplicate rate
            total_generated = len(questions)
            duplicate_rate = duplicate_count / total_generated if total_generated > 0 else 0.0

            logger.info(
                f"Generation result: {len(unique_questions)} unique, "
                f"{duplicate_count} duplicates ({duplicate_rate*100:.1f}% duplicate rate)"
            )

            # Add unique questions to our collection
            all_unique_questions.extend(unique_questions)

            # Check if we have enough questions
            if len(all_unique_questions) >= count:
                logger.info(
                    f"Successfully generated {len(all_unique_questions)} unique questions"
                )
                return all_unique_questions[:count]  # Return exactly what was requested

            # Check if we should retry
            if duplicate_rate > duplicate_retry_threshold and retry_count < max_retries:
                logger.warning(
                    f"Duplicate rate ({duplicate_rate*100:.1f}%) exceeds threshold "
                    f"({duplicate_retry_threshold*100:.1f}%), retrying..."
                )
                retry_count += 1
            else:
                # Either duplicate rate is acceptable, or we've exhausted retries
                if retry_count >= max_retries:
                    logger.warning(
                        f"Max retries ({max_retries}) reached. "
                        f"Returning {len(all_unique_questions)}/{count} unique questions."
                    )
                return all_unique_questions

        return all_unique_questions

    async def _generate_with_anti_duplicate_context(
        self,
        topic_id: str,
        count: int,
        recent_questions: List[str],
        retry_number: int
    ) -> List[Dict[str, Any]]:
        """
        Generate questions with recent context to avoid duplicates.

        Args:
            topic_id: Topic identifier
            count: Number of questions to generate
            recent_questions: Recent question texts to avoid
            retry_number: Current retry number (for logging)

        Returns:
            List of generated questions
        """
        logger.info(
            f"Generating with anti-duplicate context: "
            f"{len(recent_questions)} recent questions provided"
        )

        # Get topic configuration
        topic_config = self.config_loader.get_topic(topic_id)
        if not topic_config:
            raise ConfigurationError(f"Topic not found: {topic_id}")

        # Build prompt with anti-duplicate instructions
        prompt = self._build_prompt_with_recent_context(
            topic_config,
            count,
            recent_questions,
            retry_number
        )

        # Generate questions
        questions = await self.llm_service.generate_questions(prompt)

        logger.info(f"Generated {len(questions)} questions with anti-duplicate context")
        return questions

    def _build_prompt_with_recent_context(
        self,
        topic_config: Dict[str, Any],
        count: int,
        recent_questions: List[str],
        retry_number: int
    ) -> str:
        """
        Build prompt with recent questions context to avoid duplicates.

        Args:
            topic_config: Topic configuration
            count: Number of questions to generate
            recent_questions: Recent question texts to avoid
            retry_number: Current retry number (affects prompt strength)

        Returns:
            Prompt string with anti-duplicate instructions
        """
        # Get base prompt
        base_prompt = self._build_prompt(topic_config, "standard", None, count)

        # Add anti-duplicate section
        if recent_questions:
            recent_list = "\n".join([f"- {q}" for q in recent_questions[:20]])
            anti_dup_strength = "CRITICAL" if retry_number > 1 else "IMPORTANT"

            anti_dup_section = f"""

{anti_dup_strength}: AVOID DUPLICATE QUESTIONS

The following questions already exist for this topic. You MUST generate questions that are:
1. Semantically different (not just rephrased versions)
2. Cover different vocabulary/concepts
3. Use different sentence structures

EXISTING QUESTIONS TO AVOID:
{recent_list}

Generate {count} completely NEW questions that do NOT overlap with the above.
"""
            prompt = base_prompt + anti_dup_section
        else:
            prompt = base_prompt

        return prompt

    async def _generate_standard(
        self,
        topic_config: Dict[str, Any],
        count: int,
        db_topic_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate questions without examples.

        Args:
            topic_config: Topic configuration
            count: Number of questions to generate
            db_topic_id: Database topic ID for duplicate checking

        Returns:
            List of generated questions (filtered for duplicates)
        """
        logger.info("Generating questions using standard mode")

        prompt = self._build_prompt(topic_config, "standard", None, count)
        questions = await self.llm_service.generate_questions(prompt)

        # Filter duplicates if repository is available
        if self.repository and db_topic_id:
            questions = self._filter_duplicate_questions(questions, db_topic_id)

        logger.info(f"Generated {len(questions)} questions in standard mode")
        return questions

    async def _generate_augmented(
        self,
        topic_config: Dict[str, Any],
        examples: List[ExampleQuestion],
        count: int,
        db_topic_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate questions similar to examples.

        Args:
            topic_config: Topic configuration
            examples: Example questions
            count: Number of questions to generate
            db_topic_id: Database topic ID for duplicate checking

        Returns:
            List of generated questions (filtered for duplicates)
        """
        logger.info(f"Generating {count} questions using augment mode with {len(examples)} examples")

        prompt = self._build_prompt(topic_config, "augment", examples, count)
        questions = await self.llm_service.generate_questions(prompt)

        # Filter duplicates if repository is available
        if self.repository and db_topic_id:
            questions = self._filter_duplicate_questions(questions, db_topic_id)

        logger.info(f"Generated {len(questions)} questions in augment mode")
        return questions

    async def _generate_templated(
        self,
        topic_config: Dict[str, Any],
        examples: List[ExampleQuestion],
        count: int,
        db_topic_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate questions using example templates.

        Args:
            topic_config: Topic configuration
            examples: Example questions (used as templates)
            count: Number of questions to generate
            db_topic_id: Database topic ID for duplicate checking

        Returns:
            List of generated questions (filtered for duplicates)
        """
        logger.info(f"Generating {count} questions using template mode")

        prompt = self._build_prompt(topic_config, "template", examples, count)
        questions = await self.llm_service.generate_questions(prompt)

        # Filter duplicates if repository is available
        if self.repository and db_topic_id:
            questions = self._filter_duplicate_questions(questions, db_topic_id)

        logger.info(f"Generated {len(questions)} questions in template mode")
        return questions

    async def _generate_hybrid(
        self,
        topic_config: Dict[str, Any],
        examples: List[ExampleQuestion],
        total_count: int,
        use_ratio: float,
        db_topic_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate mix of provided and new questions.

        Args:
            topic_config: Topic configuration
            examples: Example questions (pre-filtered to unused only)
            total_count: Total number of questions needed
            use_ratio: Ratio of provided vs generated (0.3 = 30% from file)
            db_topic_id: Database topic ID for duplicate checking

        Returns:
            List of questions (mix of examples and generated, filtered for duplicates)
        """
        logger.info(
            f"Generating questions using hybrid mode: "
            f"total={total_count}, use_ratio={use_ratio}"
        )

        # Select questions from examples
        selected_examples, num_to_generate = self.example_parser.select_questions_for_hybrid(
            examples, total_count, use_ratio
        )

        # Convert selected examples to question format
        questions_from_file = [ex.to_dict() for ex in selected_examples]

        # Generate remaining questions
        if num_to_generate > 0:
            prompt = self._build_prompt(topic_config, "hybrid", examples, num_to_generate)
            generated_questions = await self.llm_service.generate_questions(prompt)

            # Filter duplicates from generated questions
            if self.repository and db_topic_id:
                generated_questions = self._filter_duplicate_questions(generated_questions, db_topic_id)
        else:
            generated_questions = []

        # Combine
        all_questions = questions_from_file + generated_questions

        logger.info(
            f"Hybrid mode complete: {len(questions_from_file)} from file, "
            f"{len(generated_questions)} generated"
        )

        return all_questions

    def _build_prompt(
        self,
        topic_config: Dict[str, Any],
        mode: str,
        examples: Optional[List[ExampleQuestion]] = None,
        count: int = 10
    ) -> str:
        """
        Build prompt for LLM.

        Args:
            topic_config: Topic configuration
            mode: Generation mode
            examples: Optional example questions
            count: Number of questions to generate

        Returns:
            Formatted prompt string
        """
        # Get base prompt template from config
        topic_type = getattr(topic_config, 'type', 'language')
        prompt_template = self.config_loader.get_prompt(topic_type, mode)

        if not prompt_template:
            # Fallback to generic prompt
            prompt_template = self._get_default_prompt(topic_type, mode)

        # Extract topic details
        topic_name = getattr(topic_config, 'name', 'Unknown')
        target_language = getattr(topic_config, 'target_language', '')
        native_language = getattr(topic_config, 'native_language', '')
        context = getattr(topic_config, 'context', '')
        scope = getattr(topic_config, 'scope', '')
        difficulty = getattr(topic_config, 'difficulty', 'intermediate')

        # Format examples if provided
        examples_text = ""
        if examples:
            examples_text = self.example_parser.format_examples_for_prompt(examples, mode)

        # Build prompt
        prompt_parts = []

        # Instructions
        prompt_parts.append(f"Generate {count} multiple-choice questions for learning.")
        prompt_parts.append(f"\nTopic: {topic_name}")

        if topic_type == "language":
            prompt_parts.append(f"Target Language: {target_language}")
            prompt_parts.append(f"Native Language: {native_language}")

        if context:
            prompt_parts.append(f"Context: {context}")

        if scope:
            prompt_parts.append(f"Scope: {scope}")

        prompt_parts.append(f"Difficulty Level: {difficulty}")

        # Add template-specific instructions
        prompt_parts.append("\n" + prompt_template)

        # Add examples
        if examples_text:
            prompt_parts.append("\n" + examples_text)

        # Output format instructions
        prompt_parts.append("\n\nOutput Format:")
        prompt_parts.append("Return a JSON array of questions with the following structure:")
        prompt_parts.append("""
[
  {
    "question_text": "The question text",
    "choice_a": "First choice",
    "choice_b": "Second choice",
    "choice_c": "Third choice",
    "choice_d": "Fourth choice",
    "correct_answer": "A",
    "explanation": "Detailed explanation in both languages if applicable",
    "difficulty": "intermediate",
    "tags": ["tag1", "tag2"]
  }
]
""")

        prompt_parts.append("\nIMPORTANT:")
        prompt_parts.append("- Return ONLY valid JSON, no additional text")
        prompt_parts.append("- Ensure all questions are unique")
        prompt_parts.append("- Make distractors plausible but clearly incorrect")
        prompt_parts.append("- Provide detailed, bilingual explanations")
        prompt_parts.append(f"- Generate exactly {count} questions")

        return "\n".join(prompt_parts)

    def _get_default_prompt(self, topic_type: str, mode: str) -> str:
        """
        Get default prompt template when not found in config.

        Args:
            topic_type: Type of topic (language, history, etc.)
            mode: Generation mode

        Returns:
            Default prompt template
        """
        if topic_type == "language":
            if mode == "augment":
                return (
                    "Generate questions similar in style and difficulty to the examples provided. "
                    "Focus on vocabulary, grammar, and practical usage. "
                    "Include bilingual explanations."
                )
            elif mode == "template":
                return (
                    "Follow the exact structure and format of the template provided. "
                    "Vary the content but maintain the question style."
                )
            else:
                return (
                    "Generate diverse language learning questions covering vocabulary, grammar, "
                    "and practical usage. Include clear bilingual explanations."
                )
        else:
            return (
                f"Generate educational multiple-choice questions about the topic. "
                f"Ensure questions are clear, accurate, and appropriate for the difficulty level."
            )

    def _filter_duplicate_questions(
        self,
        questions: List[Dict[str, Any]],
        db_topic_id: int
    ) -> List[Dict[str, Any]]:
        """
        Filter out questions that already exist in the database.

        Args:
            questions: Generated questions
            db_topic_id: Database topic ID

        Returns:
            Filtered list of questions (duplicates removed)
        """
        if not self.repository:
            return questions

        filtered = []
        duplicates_count = 0

        for question in questions:
            question_text = question.get("question_text", "")
            if not self.repository.question_exists(db_topic_id, question_text):
                filtered.append(question)
            else:
                duplicates_count += 1
                logger.debug(f"Skipping duplicate question: {question_text[:50]}...")

        if duplicates_count > 0:
            logger.info(f"Filtered out {duplicates_count} duplicate questions")

        return filtered
