"""Scheduler service for automated question generation."""

import os
from typing import Optional
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.utils.logger import get_logger
from src.database.repository import Repository
from src.services.question_generator import QuestionGenerator
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class QuestionScheduler:
    """Manages scheduled question generation jobs."""

    def __init__(
        self,
        repository: Repository,
        question_generator: QuestionGenerator,
        config_loader: ConfigLoader
    ):
        """
        Initialize the scheduler.

        Args:
            repository: Database repository
            question_generator: Question generator service
            config_loader: Configuration loader
        """
        self.repository = repository
        self.question_generator = question_generator
        self.config_loader = config_loader
        self.scheduler = AsyncIOScheduler()

        logger.info("QuestionScheduler initialized")

    async def generate_questions_job(self) -> None:
        """
        Background job to generate questions for all active topics.

        This job runs on a schedule and generates a batch of questions
        for each active topic in the database.
        """
        try:
            logger.info("Starting scheduled question generation job")

            # Get all active topics
            topics = self.repository.get_all_topics(active_only=True)

            if not topics:
                logger.warning("No active topics found for question generation")
                return

            total_generated = 0

            # Generate questions for each topic
            for topic in topics:
                try:
                    # Get topic config
                    topic_config = topic.config
                    topic_id_str = topic_config.get('id', topic.name.lower().replace(' ', '_'))

                    # Determine how many questions to generate
                    questions_per_run = int(os.getenv('QUESTIONS_PER_RUN', '5'))

                    logger.info(f"Generating {questions_per_run} questions for topic: {topic.name}")

                    # Generate questions
                    questions = await self.question_generator.generate_questions(
                        topic_id_str,
                        count=questions_per_run
                    )

                    if not questions:
                        logger.warning(f"No questions generated for topic: {topic.name}")
                        continue

                    # Save questions to database
                    saved_count = 0
                    for question_data in questions:
                        question_data['topic_id'] = topic.id
                        question_data['source'] = question_data.get('source', 'llm')

                        # Create question in database
                        self.repository.create_question(question_data)
                        saved_count += 1

                    total_generated += saved_count
                    logger.info(f"Saved {saved_count} questions for topic: {topic.name}")

                except Exception as e:
                    logger.error(f"Error generating questions for topic {topic.name}: {e}", exc_info=True)
                    continue

            logger.info(f"Question generation job completed. Total generated: {total_generated}")

        except Exception as e:
            logger.error(f"Error in question generation job: {e}", exc_info=True)

    def start(self) -> None:
        """Start the scheduler with configured jobs."""
        try:
            # Get schedule configuration from environment
            schedule_cron = os.getenv('QUESTION_GENERATION_SCHEDULE', '0 */3 * * *')  # Default: every 3 hours

            logger.info(f"Scheduling question generation with cron: {schedule_cron}")

            # Add job with cron trigger
            self.scheduler.add_job(
                self.generate_questions_job,
                CronTrigger.from_crontab(schedule_cron),
                id='generate_questions',
                name='Generate Questions Job',
                replace_existing=True
            )

            # Start the scheduler
            self.scheduler.start()
            logger.info("Scheduler started successfully")

        except Exception as e:
            logger.error(f"Error starting scheduler: {e}", exc_info=True)
            raise

    def stop(self) -> None:
        """Stop the scheduler gracefully."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}", exc_info=True)

    async def run_manual_generation(self, topic_id: Optional[int] = None, count: int = 5) -> int:
        """
        Manually trigger question generation.

        Args:
            topic_id: Optional specific topic ID to generate for (None = all topics)
            count: Number of questions to generate per topic

        Returns:
            Total number of questions generated
        """
        try:
            logger.info(f"Manual question generation triggered (topic_id={topic_id}, count={count})")

            # Get topics
            if topic_id:
                topic = self.repository.get_topic(topic_id)
                topics = [topic] if topic else []
            else:
                topics = self.repository.get_all_topics(active_only=True)

            if not topics:
                logger.warning("No topics found for manual generation")
                return 0

            total_generated = 0

            # Generate questions for each topic
            for topic in topics:
                try:
                    topic_config = topic.config
                    topic_id_str = topic_config.get('id', topic.name.lower().replace(' ', '_'))

                    logger.info(f"Generating {count} questions for topic: {topic.name}")

                    questions = await self.question_generator.generate_questions(
                        topic_id_str,
                        count=count
                    )

                    if not questions:
                        continue

                    # Save questions
                    for question_data in questions:
                        question_data['topic_id'] = topic.id
                        question_data['source'] = question_data.get('source', 'llm')
                        self.repository.create_question(question_data)
                        total_generated += 1

                    logger.info(f"Saved {len(questions)} questions for topic: {topic.name}")

                except Exception as e:
                    logger.error(f"Error in manual generation for topic {topic.name}: {e}", exc_info=True)
                    continue

            logger.info(f"Manual generation completed. Total generated: {total_generated}")
            return total_generated

        except Exception as e:
            logger.error(f"Error in manual question generation: {e}", exc_info=True)
            return 0
