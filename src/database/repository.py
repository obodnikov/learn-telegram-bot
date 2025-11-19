"""Database repository for all data access operations."""

import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from src.database.models import (
    Base,
    User,
    UserSettings,
    Topic,
    Question,
    UserProgress,
    QuestionAnalytics,
    TopicHistory,
    ExampleFileValidation,
    QuestionSource,
    ValidationStatus
)
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseError

logger = get_logger(__name__)


class Repository:
    """Database repository for all data access operations."""

    def __init__(self, db_url: str = "sqlite:///learning_bot.db"):
        """
        Initialize repository with database connection.

        Args:
            db_url: Database connection URL
        """
        self.db_url = db_url
        try:
            self.engine = create_engine(db_url, echo=False)
            self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
            logger.info(f"Repository initialized with database: {db_url}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session context manager.

        Yields:
            SQLAlchemy session

        Raises:
            DatabaseError: If session operations fail
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            session.close()

    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseError(f"Table creation failed: {e}")

    # User operations

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Get user by telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(User).filter(User.telegram_id == telegram_id).first()

    def create_user(self, telegram_id: int, native_language: str) -> User:
        """
        Create new user.

        Args:
            telegram_id: Telegram user ID
            native_language: User's native language

        Returns:
            Created User object
        """
        with self.get_session() as session:
            user = User(
                telegram_id=telegram_id,
                native_language=native_language,
                created_at=datetime.utcnow()
            )
            session.add(user)
            session.flush()
            session.refresh(user)
            logger.info(f"Created user with telegram_id: {telegram_id}")
            return user

    def get_or_create_user(self, telegram_id: int, native_language: str) -> User:
        """
        Get existing user or create new one.

        Args:
            telegram_id: Telegram user ID
            native_language: User's native language

        Returns:
            User object
        """
        user = self.get_user_by_telegram_id(telegram_id)
        if user is None:
            user = self.create_user(telegram_id, native_language)
        return user

    # User Settings operations

    def get_user_settings(self, user_id: int) -> Optional[UserSettings]:
        """
        Get user settings by user ID.

        Args:
            user_id: Internal user ID (not telegram_id)

        Returns:
            UserSettings object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    def create_user_settings(self, user_id: int, questions_per_batch: Optional[int] = None) -> UserSettings:
        """
        Create user settings.

        Args:
            user_id: Internal user ID (not telegram_id)
            questions_per_batch: Number of questions per batch (None = use topic default)

        Returns:
            Created UserSettings object
        """
        with self.get_session() as session:
            settings = UserSettings(
                user_id=user_id,
                questions_per_batch=questions_per_batch,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(settings)
            session.flush()
            session.refresh(settings)
            logger.info(f"Created settings for user {user_id}: questions_per_batch={questions_per_batch}")
            return settings

    def update_user_settings(
        self,
        user_id: int,
        questions_per_batch: Optional[int] = None
    ) -> UserSettings:
        """
        Update or create user settings.

        Args:
            user_id: Internal user ID (not telegram_id)
            questions_per_batch: Number of questions per batch (None = use topic default)

        Returns:
            Updated UserSettings object
        """
        with self.get_session() as session:
            settings = session.query(UserSettings).filter(UserSettings.user_id == user_id).first()

            if settings:
                # Update existing settings
                settings.questions_per_batch = questions_per_batch
                settings.updated_at = datetime.utcnow()
                session.flush()
                session.refresh(settings)
                logger.info(f"Updated settings for user {user_id}: questions_per_batch={questions_per_batch}")
            else:
                # Create new settings
                settings = UserSettings(
                    user_id=user_id,
                    questions_per_batch=questions_per_batch,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(settings)
                session.flush()
                session.refresh(settings)
                logger.info(f"Created settings for user {user_id}: questions_per_batch={questions_per_batch}")

            return settings

    def get_or_create_user_settings(self, user_id: int) -> UserSettings:
        """
        Get existing user settings or create default ones.

        Args:
            user_id: Internal user ID (not telegram_id)

        Returns:
            UserSettings object
        """
        settings = self.get_user_settings(user_id)
        if settings is None:
            settings = self.create_user_settings(user_id)
        return settings

    # Topic operations

    def get_all_topics(self, active_only: bool = True) -> List[Topic]:
        """
        Get all topics.

        Args:
            active_only: Return only active topics

        Returns:
            List of Topic objects
        """
        with self.get_session() as session:
            query = session.query(Topic)
            if active_only:
                query = query.filter(Topic.is_active == True)
            return query.all()

    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """
        Get topic by ID.

        Args:
            topic_id: Topic ID

        Returns:
            Topic object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(Topic).filter(Topic.id == topic_id).first()

    def get_topic_by_name(self, name: str) -> Optional[Topic]:
        """
        Get topic by name.

        Args:
            name: Topic name

        Returns:
            Topic object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(Topic).filter(Topic.name == name).first()

    def create_topic(self, name: str, type: str, config: dict, is_active: bool = True) -> Topic:
        """
        Create new topic.

        Args:
            name: Topic name
            type: Topic type (language, history, etc.)
            config: Topic configuration dictionary
            is_active: Whether topic is active

        Returns:
            Created Topic object
        """
        with self.get_session() as session:
            topic = Topic(
                name=name,
                type=type,
                config=config,
                is_active=is_active,
                created_at=datetime.utcnow()
            )
            session.add(topic)
            session.flush()
            session.refresh(topic)
            logger.info(f"Created topic: {name}")
            return topic

    def update_topic(self, topic_id: int, config: dict, is_active: bool = True) -> Optional[Topic]:
        """
        Update existing topic.

        Args:
            topic_id: Topic ID to update
            config: New topic configuration dictionary
            is_active: Whether topic is active

        Returns:
            Updated Topic object if found, None otherwise
        """
        with self.get_session() as session:
            topic = session.query(Topic).filter(Topic.id == topic_id).first()
            if topic:
                topic.config = config
                topic.is_active = is_active
                session.flush()
                session.refresh(topic)
                logger.info(f"Updated topic: {topic.name}")
            return topic

    # Question operations

    def create_question(self, question_data: Dict[str, Any]) -> Question:
        """
        Create new question.

        Args:
            question_data: Dictionary containing question fields

        Returns:
            Created Question object
        """
        with self.get_session() as session:
            question = Question(
                topic_id=question_data['topic_id'],
                question_text=question_data['question_text'],
                choice_a=question_data['choice_a'],
                choice_b=question_data['choice_b'],
                choice_c=question_data['choice_c'],
                choice_d=question_data['choice_d'],
                correct_answer=question_data['correct_answer'],
                explanation=question_data['explanation'],
                difficulty=question_data['difficulty'],
                tags=question_data.get('tags', []),
                source=question_data.get('source', QuestionSource.LLM.value),
                source_file=question_data.get('source_file'),
                created_at=datetime.utcnow(),
                quality_score=question_data.get('quality_score', 0.5)
            )
            session.add(question)
            session.flush()

            # Create analytics entry
            analytics = QuestionAnalytics(
                question_id=question.id,
                total_times_shown=0,
                total_correct=0,
                total_incorrect=0,
                success_rate=0.0,
                last_updated_at=datetime.utcnow(),
                needs_review=False
            )
            session.add(analytics)
            session.flush()
            session.refresh(question)

            logger.info(f"Created question ID: {question.id} for topic_id: {question.topic_id}")
            return question

    def get_question(self, question_id: int) -> Optional[Question]:
        """
        Get question by ID.

        Args:
            question_id: Question ID

        Returns:
            Question object if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(Question).filter(Question.id == question_id).first()

    def get_questions_for_topic(self, topic_id: int) -> List[Question]:
        """
        Get all questions for a topic.

        Args:
            topic_id: Topic ID

        Returns:
            List of Question objects
        """
        with self.get_session() as session:
            return session.query(Question).filter(Question.topic_id == topic_id).all()

    def question_exists(self, topic_id: int, question_text: str) -> bool:
        """
        Check if a question with the same text already exists for a topic.

        Args:
            topic_id: Topic ID
            question_text: Question text to check

        Returns:
            True if question exists, False otherwise
        """
        with self.get_session() as session:
            existing = session.query(Question).filter(
                and_(
                    Question.topic_id == topic_id,
                    Question.question_text == question_text
                )
            ).first()
            return existing is not None

    def get_next_question(
        self,
        user_id: int,
        topic_id: int,
        unseen_shown: int = 0,
        unseen_target: int = 0,
        exclude_question_ids: list[int] = None
    ) -> Optional[Question]:
        """
        Get next question based on spaced repetition algorithm with configurable unseen ratio.

        Selection Logic:
        - If unseen_shown < unseen_target: Prioritize unseen questions (if available)
        - Otherwise: Follow spaced repetition priority (due → non-mastered)

        Spaced Repetition Priority:
        1. Questions due for review (next_review_at <= now, consecutive_correct < 2) - random
        2. Questions with consecutive_correct < 2 (not mastered) - random

        Excludes questions with consecutive_correct >= 2 (mastered/known)
        Excludes questions in exclude_question_ids list (already shown in session)

        Args:
            user_id: User ID
            topic_id: Topic ID
            unseen_shown: Number of unseen questions shown in current session
            unseen_target: Target number of unseen questions for session (e.g., 40% of batch)
            exclude_question_ids: List of question IDs to exclude (already shown in session)

        Returns:
            Question object or None if no questions available
        """
        with self.get_session() as session:
            now = datetime.utcnow()
            exclude_question_ids = exclude_question_ids or []

            # Get all questions for topic
            all_questions = session.query(Question).filter(
                Question.topic_id == topic_id
            ).all()

            if not all_questions:
                return None

            # Filter out excluded questions (already shown in session)
            all_questions = [q for q in all_questions if q.id not in exclude_question_ids]

            if not all_questions:
                logger.info(
                    f"No available questions for topic {topic_id} "
                    f"(all {len(exclude_question_ids)} available questions already shown in session)"
                )
                return None

            all_question_ids = [q.id for q in all_questions]

            # Get user progress for all questions
            progress_map = {}
            progresses = session.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.question_id.in_(all_question_ids)
                )
            ).all()

            for prog in progresses:
                progress_map[prog.question_id] = prog

            # Build question pools
            unseen_questions = []
            due_questions = []
            non_mastered = []

            for q in all_questions:
                prog = progress_map.get(q.id)

                if not prog:
                    # Never seen before
                    unseen_questions.append(q)
                elif prog.consecutive_correct < 2:
                    # Seen but not mastered
                    if prog.next_review_at and prog.next_review_at <= now:
                        due_questions.append(q)
                    non_mastered.append(q)
                # Else: mastered (consecutive_correct >= 2), excluded

            # Decision logic: Check if we need more unseen questions
            need_unseen = unseen_shown < unseen_target

            if need_unseen and unseen_questions:
                # Priority: Unseen questions (to meet quota)
                selected = random.choice(unseen_questions)
                logger.info(
                    f"Selected unseen question ID: {selected.id} "
                    f"(random from {len(unseen_questions)} unseen, "
                    f"progress: {unseen_shown + 1}/{unseen_target})"
                )
                return selected

            # Otherwise, follow spaced repetition priority
            if due_questions:
                # Priority 1: Questions due for review
                selected = random.choice(due_questions)
                logger.info(
                    f"Selected due question ID: {selected.id} "
                    f"(random from {len(due_questions)} due)"
                )
                return selected

            if non_mastered:
                # Priority 2: Non-mastered questions (not yet due)
                selected = random.choice(non_mastered)
                logger.info(
                    f"Selected non-mastered question ID: {selected.id} "
                    f"(random from {len(non_mastered)} non-mastered)"
                )
                return selected

            # Fallback: If no non-mastered but have unseen (unseen quota already met)
            if unseen_questions:
                selected = random.choice(unseen_questions)
                logger.info(
                    f"Selected unseen question ID: {selected.id} "
                    f"(fallback: random from {len(unseen_questions)} unseen, quota met)"
                )
                return selected

            # All questions are mastered (consecutive_correct >= 2)
            logger.info(
                f"All questions for topic {topic_id} are mastered (consecutive_correct >= 2)"
            )
            return None

    def is_question_unseen(self, user_id: int, question_id: int) -> bool:
        """
        Check if a question has been seen by the user before.

        Args:
            user_id: User ID
            question_id: Question ID

        Returns:
            True if question has never been seen by user, False otherwise
        """
        with self.get_session() as session:
            progress = session.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.question_id == question_id
                )
            ).first()
            return progress is None

    def check_duplicate_question_fuzzy(
        self,
        topic_id: int,
        question_text: str,
        threshold: float = 0.85
    ) -> tuple[bool, float]:
        """
        Check if question is duplicate using fuzzy string matching.

        Args:
            topic_id: Topic ID to check within
            question_text: Question text to check
            threshold: Similarity threshold (0.0-1.0), default 0.85

        Returns:
            Tuple of (is_duplicate, max_similarity_score)
            - is_duplicate: True if any existing question exceeds threshold
            - max_similarity_score: Highest similarity found (0.0-1.0)
        """
        from difflib import SequenceMatcher

        with self.get_session() as session:
            # Get all questions for this topic
            existing_questions = session.query(Question).filter(
                Question.topic_id == topic_id
            ).all()

            if not existing_questions:
                return False, 0.0

            max_similarity = 0.0

            # Check fuzzy similarity against each existing question
            for existing_q in existing_questions:
                similarity = SequenceMatcher(
                    None,
                    question_text.lower().strip(),
                    existing_q.question_text.lower().strip()
                ).ratio()

                max_similarity = max(max_similarity, similarity)

                # Early exit if we find a duplicate
                if similarity > threshold:
                    logger.debug(
                        f"Duplicate found: similarity={similarity:.2f} "
                        f"(threshold={threshold})\n"
                        f"New: {question_text[:50]}...\n"
                        f"Existing: {existing_q.question_text[:50]}..."
                    )
                    return True, similarity

            return False, max_similarity

    def get_recent_questions(
        self,
        topic_id: int,
        limit: int = 20
    ) -> list[str]:
        """
        Get recent question texts for LLM context (to avoid duplicates).

        Args:
            topic_id: Topic ID
            limit: Number of recent questions to fetch (default: 20)

        Returns:
            List of question texts, ordered by creation date (newest first)
        """
        with self.get_session() as session:
            questions = session.query(Question).filter(
                Question.topic_id == topic_id
            ).order_by(
                Question.created_at.desc()
            ).limit(limit).all()

            return [q.question_text for q in questions]

    # Progress operations

    def update_progress(
        self,
        user_id: int,
        question_id: int,
        is_correct: bool,
        response_time: Optional[float] = None
    ) -> None:
        """
        Update user progress for a question using spaced repetition.

        Intervals:
        - Correct: multiply interval by 2 (1h, 2h, 4h, 8h, 16h, etc.)
        - Incorrect: reset to 1 hour

        Args:
            user_id: User ID
            question_id: Question ID
            is_correct: Whether answer was correct
            response_time: Response time in seconds
        """
        with self.get_session() as session:
            # Get or create progress
            progress = session.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.question_id == question_id
                )
            ).first()

            now = datetime.utcnow()

            if progress is None:
                # Create new progress
                progress = UserProgress(
                    user_id=user_id,
                    question_id=question_id,
                    times_shown=1,
                    times_correct=1 if is_correct else 0,
                    times_incorrect=0 if is_correct else 1,
                    consecutive_correct=1 if is_correct else 0,
                    last_shown_at=now,
                    next_review_at=now + timedelta(hours=1 if is_correct else 1),
                    average_response_time=response_time
                )
                session.add(progress)
            else:
                # Update existing progress
                progress.times_shown += 1
                progress.last_shown_at = now

                if is_correct:
                    progress.times_correct += 1
                    progress.consecutive_correct += 1

                    # Spaced repetition: double interval (min 1h, max ~30 days)
                    interval_hours = min(2 ** progress.consecutive_correct, 720)  # max 30 days
                    progress.next_review_at = now + timedelta(hours=interval_hours)
                else:
                    progress.times_incorrect += 1
                    progress.consecutive_correct = 0

                    # Reset to 1 hour
                    progress.next_review_at = now + timedelta(hours=1)

                # Update average response time
                if response_time is not None:
                    if progress.average_response_time is None:
                        progress.average_response_time = response_time
                    else:
                        # Rolling average
                        progress.average_response_time = (
                            progress.average_response_time * 0.7 + response_time * 0.3
                        )

            logger.info(
                f"Updated progress for user {user_id}, question {question_id}: "
                f"correct={is_correct}, consecutive={progress.consecutive_correct}"
            )

    # Analytics operations

    def get_user_stats(self, user_id: int, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get user statistics.

        Args:
            user_id: User ID
            topic_id: Optional topic ID to filter by

        Returns:
            Dictionary with statistics including:
            - total_questions: Total questions in topic/all topics
            - questions_seen: Questions user has encountered
            - questions_not_seen: Questions never encountered
            - total_correct: Total correct answers
            - total_incorrect: Total incorrect answers
            - accuracy: Percentage of correct answers
            - questions_known: Questions with consecutive_correct >= 2 (mastered)
            - questions_learning: Questions seen but not yet known
            - questions_due: Questions due for review now
            - average_response_time: Average time to answer
            - last_activity: Most recent activity timestamp
        """
        with self.get_session() as session:
            # Get total questions count
            total_questions_query = session.query(Question)
            if topic_id:
                total_questions_query = total_questions_query.filter(Question.topic_id == topic_id)
            total_questions = total_questions_query.count()

            # Get user progress
            query = session.query(UserProgress).filter(UserProgress.user_id == user_id)

            if topic_id:
                # Join with Question to filter by topic
                query = query.join(Question).filter(Question.topic_id == topic_id)

            progresses = query.all()

            if not progresses:
                return {
                    'total_questions': total_questions,
                    'questions_seen': 0,
                    'questions_not_seen': total_questions,
                    'total_correct': 0,
                    'total_incorrect': 0,
                    'accuracy': 0.0,
                    'questions_known': 0,
                    'questions_learning': 0,
                    'questions_due': 0,
                    'average_response_time': None,
                    'last_activity': None
                }

            total_correct = sum(p.times_correct for p in progresses)
            total_incorrect = sum(p.times_incorrect for p in progresses)
            total_attempts = total_correct + total_incorrect

            response_times = [p.average_response_time for p in progresses if p.average_response_time]
            avg_response_time = sum(response_times) / len(response_times) if response_times else None

            # Known = consecutive_correct >= 2 (matches mastery exclusion in get_next_question)
            questions_known = sum(1 for p in progresses if p.consecutive_correct >= 2)
            questions_seen = len(progresses)
            questions_learning = questions_seen - questions_known

            # Questions due for review
            now = datetime.utcnow()
            questions_due = sum(
                1 for p in progresses
                if p.next_review_at and p.next_review_at <= now and p.consecutive_correct < 2
            )

            # Last activity
            last_shown_times = [p.last_shown_at for p in progresses if p.last_shown_at]
            last_activity = max(last_shown_times) if last_shown_times else None

            return {
                'total_questions': total_questions,
                'questions_seen': questions_seen,
                'questions_not_seen': total_questions - questions_seen,
                'total_correct': total_correct,
                'total_incorrect': total_incorrect,
                'accuracy': total_correct / total_attempts if total_attempts > 0 else 0.0,
                'questions_known': questions_known,
                'questions_learning': questions_learning,
                'questions_due': questions_due,
                'average_response_time': avg_response_time,
                'last_activity': last_activity
            }

    def update_question_analytics(self, question_id: int) -> None:
        """
        Update question analytics based on user progress.

        Args:
            question_id: Question ID
        """
        with self.get_session() as session:
            # Get analytics
            analytics = session.query(QuestionAnalytics).filter(
                QuestionAnalytics.question_id == question_id
            ).first()

            if not analytics:
                analytics = QuestionAnalytics(
                    question_id=question_id,
                    total_times_shown=0,
                    total_correct=0,
                    total_incorrect=0,
                    success_rate=0.0,
                    last_updated_at=datetime.utcnow(),
                    needs_review=False
                )
                session.add(analytics)

            # Aggregate from user progress
            progresses = session.query(UserProgress).filter(
                UserProgress.question_id == question_id
            ).all()

            if progresses:
                analytics.total_times_shown = sum(p.times_shown for p in progresses)
                analytics.total_correct = sum(p.times_correct for p in progresses)
                analytics.total_incorrect = sum(p.times_incorrect for p in progresses)

                total_attempts = analytics.total_correct + analytics.total_incorrect
                analytics.success_rate = (
                    analytics.total_correct / total_attempts if total_attempts > 0 else 0.0
                )

                # Calculate average response time
                response_times = [p.average_response_time for p in progresses if p.average_response_time]
                analytics.average_response_time = (
                    sum(response_times) / len(response_times) if response_times else None
                )

                # Mark for review if success rate is low
                analytics.needs_review = analytics.success_rate < 0.4 and total_attempts >= 5

                analytics.last_updated_at = datetime.utcnow()

                logger.info(
                    f"Updated analytics for question {question_id}: "
                    f"success_rate={analytics.success_rate:.2f}, needs_review={analytics.needs_review}"
                )

    def get_low_quality_questions(self, threshold: float = 0.4, min_attempts: int = 5) -> List[Question]:
        """
        Get questions with low success rate.

        Args:
            threshold: Success rate threshold (0-1)
            min_attempts: Minimum number of attempts

        Returns:
            List of Question objects
        """
        with self.get_session() as session:
            analytics = session.query(QuestionAnalytics).filter(
                and_(
                    QuestionAnalytics.success_rate < threshold,
                    QuestionAnalytics.total_times_shown >= min_attempts
                )
            ).all()

            question_ids = [a.question_id for a in analytics]
            questions = session.query(Question).filter(Question.id.in_(question_ids)).all()

            return questions

    # Topic History operations

    def is_topic_finished(self, user_id: int, topic_id: int) -> bool:
        """
        Check if a topic is finished (all questions mastered).

        Args:
            user_id: User ID
            topic_id: Topic ID

        Returns:
            True if all questions have consecutive_correct >= 2, False otherwise
        """
        with self.get_session() as session:
            # Get all questions for the topic
            all_questions = session.query(Question).filter(
                Question.topic_id == topic_id
            ).all()

            if not all_questions:
                return False

            all_question_ids = [q.id for q in all_questions]

            # Get user progress for all questions
            progresses = session.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.question_id.in_(all_question_ids)
                )
            ).all()

            # Check if user has seen all questions and mastered them
            if len(progresses) != len(all_questions):
                return False

            # All questions must have consecutive_correct >= 2
            return all(p.consecutive_correct >= 2 for p in progresses)

    def get_topic_history(self, user_id: int, topic_id: Optional[int] = None) -> List[TopicHistory]:
        """
        Get topic completion history for a user.

        Args:
            user_id: User ID
            topic_id: Optional topic ID to filter by

        Returns:
            List of TopicHistory objects ordered by completion_date (newest first)
        """
        with self.get_session() as session:
            query = session.query(TopicHistory).filter(TopicHistory.user_id == user_id)

            if topic_id is not None:
                query = query.filter(TopicHistory.topic_id == topic_id)

            return query.order_by(TopicHistory.completion_date.desc()).all()

    def archive_topic_progress(self, user_id: int, topic_id: int) -> TopicHistory:
        """
        Archive current topic progress to history before reset.

        Args:
            user_id: User ID
            topic_id: Topic ID

        Returns:
            Created TopicHistory object

        Raises:
            DatabaseError: If topic is not finished or no progress exists
        """
        with self.get_session() as session:
            # Get current stats for the topic
            stats = self.get_user_stats(user_id, topic_id)

            if stats['questions_seen'] == 0:
                raise DatabaseError("Cannot archive topic with no progress")

            # Calculate next attempt number
            existing_history = session.query(TopicHistory).filter(
                and_(
                    TopicHistory.user_id == user_id,
                    TopicHistory.topic_id == topic_id
                )
            ).all()
            attempt_number = len(existing_history) + 1

            # Create history record
            history = TopicHistory(
                user_id=user_id,
                topic_id=topic_id,
                completion_date=datetime.utcnow(),
                questions_total=stats['total_questions'],
                questions_correct=stats['total_correct'],
                questions_incorrect=stats['total_incorrect'],
                accuracy_percentage=stats['accuracy'] * 100,
                questions_known=stats['questions_known'],
                attempt_number=attempt_number
            )
            session.add(history)
            session.flush()
            session.refresh(history)

            logger.info(
                f"Archived topic {topic_id} progress for user {user_id}: "
                f"attempt {attempt_number}, accuracy {stats['accuracy']*100:.1f}%"
            )

            return history

    def reset_topic_progress(self, user_id: int, topic_id: int) -> int:
        """
        Reset user progress for all questions in a topic.

        Args:
            user_id: User ID
            topic_id: Topic ID

        Returns:
            Number of progress records deleted

        Raises:
            DatabaseError: If topic is not finished
        """
        if not self.is_topic_finished(user_id, topic_id):
            raise DatabaseError("Cannot reset topic that is not finished")

        with self.get_session() as session:
            # Get all questions for the topic
            all_questions = session.query(Question).filter(
                Question.topic_id == topic_id
            ).all()

            if not all_questions:
                return 0

            all_question_ids = [q.id for q in all_questions]

            # Delete all user progress for these questions
            deleted_count = session.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.question_id.in_(all_question_ids)
                )
            ).delete(synchronize_session=False)

            logger.info(
                f"Reset topic {topic_id} progress for user {user_id}: "
                f"deleted {deleted_count} progress records"
            )

            return deleted_count

    # Example file validation operations

    def log_validation(
        self,
        file_path: str,
        status: ValidationStatus,
        errors: List[str],
        question_count: int
    ) -> None:
        """
        Log example file validation result.

        Args:
            file_path: Path to example file
            status: Validation status
            errors: List of validation errors
            question_count: Number of questions in file
        """
        with self.get_session() as session:
            validation = session.query(ExampleFileValidation).filter(
                ExampleFileValidation.file_path == file_path
            ).first()

            if validation:
                validation.validation_status = status.value
                validation.validation_errors = errors
                validation.last_validated_at = datetime.utcnow()
                validation.question_count = question_count
            else:
                validation = ExampleFileValidation(
                    file_path=file_path,
                    validation_status=status.value,
                    validation_errors=errors,
                    last_validated_at=datetime.utcnow(),
                    question_count=question_count
                )
                session.add(validation)

            logger.info(f"Logged validation for {file_path}: {status.value}")
